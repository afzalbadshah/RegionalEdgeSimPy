import os
import torch
import torch.nn as nn
import torch.optim as optim
from scheduler.base_scheduler import BaseScheduler
from matplotlib import pyplot as plt
import numpy as np
from config.metrics import (
    calculate_transmission_cost,
    calculate_processing_cost,
    calculate_propagation_delay,
    calculate_edge_energy,
    calculate_regional_energy,
    calculate_cloud_energy
)
from config.config import SERVER_CONFIG

def util_score(u: float) -> float:
    
    if u < 50.0:
        return 0.0
    elif u < 60.0:
        return 5.0
    elif u < 70.0:
        return 10.0
    elif u < 80.0:
        return -10.0
    elif u < 90.0:
        return -20.0
    else:
        return -30.0

class ActorCritic(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.shared = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        self.policy_head = nn.Linear(hidden_dim, output_dim)
        self.value_head = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        features = self.shared(x)
        return self.policy_head(features), self.value_head(features)

class PpoMEScheduler(BaseScheduler):
    def __init__(self, buffer_threshold: int = 20, lr: float = 1e-3, hidden_dim: int = 64):
        super().__init__()
        self.buffer_threshold = buffer_threshold
        self.lr = lr
        self.hidden_dim = hidden_dim
        self.K_epochs = 4
        self.eps_clip = 0.2
        self.gamma = 0.99

        self.tier_names = ["Edge", "Regional", "Cloud"]
        self.training_mode = True
        self.experience_buffer = []
        self.episode_rewards = []
        self.actor_losses = []
        self.critic_losses = []
        self.action_distribution_log = []
        self.model = None
        self.optimizer = None
        self.mse_loss = nn.MSELoss()
        self.model_path = "ppo_me_model.pth"

        # pointers for sequential fill
        self.edge_idx = 0
        self.reg_idx = 0
        self.cloud_idx = 0
        self.phase = 0  # 0=edge,1=regional,2=cloud

    def _get_energy(self, task, server):
        tier = server.name.split('_')[0]
        if tier == "Edge": return calculate_edge_energy(task.data_size_kb)
        if tier == "Regional": return calculate_regional_energy(task.data_size_kb)
        return calculate_cloud_energy(task.data_size_kb)

    def _ensure_model(self):
        N = len(self.servers_list)
        input_dim = 6 * N
        if self.model is None:
            self.model = ActorCritic(input_dim, self.hidden_dim, N)
            self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
            if os.path.isfile(self.model_path):
                try:
                    self.model.load_state_dict(torch.load(self.model_path))
                except RuntimeError:
                    pass

    def _construct_state(self, task):
        state = []
        for sv in self.servers_list:
            cpu, _, mem = sv.utilization()
            cong = sv.congestion()
            cost = calculate_processing_cost(task.cpu_demand, sv.cost) + calculate_transmission_cost(task.data_size_kb, sv.cost)
            delay = calculate_propagation_delay(sv.name) / 1000.0
            energy = self._get_energy(task, sv)
            state.extend([cpu, mem, cong, cost, delay, energy])
        return state

    def _compute_reward(self, delay, cost, congestion, cpu_util, mem_util, energy, server_idx):
        if delay < 0.005: D_r = 10
        elif delay < 0.02: D_r = 5
        else: D_r = -10
        if cost < 0.5: C_r = 10
        elif cost < 1.5: C_r = 5
        else: C_r = -10
        Con_r = 10 if congestion < 30 else (0 if congestion < 50 else -10)
        E_r = 10 if energy < 0.1 else (0 if energy < 0.3 else -10)
        cpu_r = util_score(cpu_util)
        mem_r = util_score(mem_util)
        over_cpu = max(0.0, cpu_util - 70.0)
        over_mem = max(0.0, mem_util - 70.0)
        over_penalty = -50.0 * (over_cpu + over_mem)
        edge_count = SERVER_CONFIG['Edge']['num_datacenters']
        reg_count  = SERVER_CONFIG['Regional']['num_datacenters']
        if server_idx < edge_count: tier_bias = 5.0
        elif server_idx < edge_count + reg_count: tier_bias = 1.0
        else: tier_bias = 0.0
        base = 0.2*D_r + 0.2*C_r + 0.15*Con_r + 0.15*E_r + 0.15*cpu_r + 0.15*mem_r
        return base + over_penalty + tier_bias

    def train_ppo(self):
        states, actions, rewards = zip(*self.experience_buffer)
        states  = torch.FloatTensor(states)
        actions = torch.LongTensor(actions).view(-1)
        rewards = torch.FloatTensor(rewards).view(-1)
        for _ in range(self.K_epochs):
            logits, values = self.model(states)
            dist = torch.distributions.Categorical(logits=logits)
            log_probs = dist.log_prob(actions)
            advantages = rewards - values.squeeze().detach()
            actor_loss  = -(log_probs * advantages).mean()
            critic_loss = self.mse_loss(values.squeeze(), rewards)
            loss        = actor_loss + critic_loss
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        avg_reward = rewards.mean().item()
        self.episode_rewards.append(avg_reward)
        self.actor_losses.append(actor_loss.item())
        self.critic_losses.append(critic_loss.item())

        # compute mean action probs across batch
        probs = dist.probs.mean(dim=0).detach().cpu().numpy()
        probs /= probs.sum()
        tier_map = []
        for sv in self.servers_list:
            t = sv.name.split('_')[0]
            tier_map.append({"Edge":0, "Regional":1}.get(t, 2))
        ad = [0.0, 0.0, 0.0]
        for idx, p in enumerate(probs):
            ad[tier_map[idx]] += p
        self.action_distribution_log.append(ad)

        self.experience_buffer.clear()
        torch.save(self.model.state_dict(), self.model_path)

        # plot & save
        plt.figure()
        plt.plot(self.episode_rewards)
        plt.xlabel('Episodes'); plt.ylabel('Average Reward')
        plt.title('Average Reward per Episode'); plt.grid()
        plt.savefig('visualization/train/average_reward.png'); plt.close()
        plt.figure()
        plt.plot(self.actor_losses,  label='Actor Loss')
        plt.plot(self.critic_losses, label='Critic Loss')
        plt.xlabel('Episodes'); plt.ylabel('Loss')
        plt.title('Loss Convergence'); plt.legend(); plt.grid()
        plt.savefig('visualization/train/loss_convergence.png'); plt.close()
        arr = np.array(self.action_distribution_log)
        plt.figure()
        plt.stackplot(range(len(arr)), arr.T, labels=['Edge','Regional','Cloud'])
        plt.xlabel('Episodes'); plt.ylabel('Action Ratio')
        plt.title('Action Distribution Over Time'); plt.legend(); plt.grid()
        plt.savefig('visualization/train/action_distribution.png'); plt.close()

    def schedule(self, tasks, servers, current_time):
        self.servers_list = []
        for tier in self.tier_names:
            ts = [s for s in servers if s.name.startswith(tier)]
            ts.sort(key=lambda s: int(s.name.split('_')[1]))
            self.servers_list.extend(ts)
        self._ensure_model()
        edge_count = sum(s.name.startswith('Edge')    for s in self.servers_list)
        reg_count  = sum(s.name.startswith('Regional')for s in self.servers_list)
        cloud_count = len(self.servers_list) - edge_count - reg_count
        assignments=[]; TH=70.0
        for task in tasks:
            if self.phase==0:
                if self.edge_idx<edge_count:
                    if self.servers_list[self.edge_idx].utilization()[0]>=TH: self.edge_idx+=1
                    if self.edge_idx>=edge_count: self.phase=1
                allowed = [self.edge_idx] if self.phase==0 and self.edge_idx<edge_count else []
            if self.phase==1:
                if self.reg_idx<reg_count:
                    idx=edge_count+self.reg_idx
                    if self.servers_list[idx].utilization()[0]>=TH: self.reg_idx+=1
                    if self.reg_idx>=reg_count: self.phase=2
                allowed=[edge_count+self.reg_idx] if self.phase==1 and self.reg_idx<reg_count else []
            if self.phase==2:
                start=edge_count+reg_count
                allowed=[start+self.cloud_idx] if self.cloud_idx<cloud_count else []
            if not allowed:
                if self.phase==0: allowed=list(range(edge_count))
                elif self.phase==1: allowed=list(range(edge_count,edge_count+reg_count))
                else: allowed=list(range(edge_count+reg_count,len(self.servers_list)))
            state=self._construct_state(task)
            logits,_=self.model(torch.FloatTensor([state])); logits=logits[0]
            mask=torch.full_like(logits,float('-inf'))
            for i in allowed: mask[i]=0.0
            dist=torch.distributions.Categorical(logits=logits+mask)
            action=dist.sample().item()
            if self.phase==2 and action>=edge_count+reg_count: self.cloud_idx+=1
            srv=self.servers_list[action]
            if srv.can_allocate(task.cpu_demand,task.storage_demand,task.memory_demand):
                srv.allocate(task.id,task.cpu_demand,task.storage_demand,task.memory_demand,current_time+srv.latency)
                task.set_server(srv.name); assignments.append((task,srv))
                cpu,_,mem=srv.utilization(); energy=self._get_energy(task,srv)
                reward=self._compute_reward(
                    delay=calculate_propagation_delay(srv.name),
                    cost=(calculate_processing_cost(task.cpu_demand,srv.cost)+calculate_transmission_cost(task.data_size_kb,srv.cost)),
                    congestion=srv.congestion(), cpu_util=cpu, mem_util=mem, energy=energy, server_idx=action)
                self.experience_buffer.append((state,action,reward))
            else:
                task.fail()
        if self.training_mode and len(self.experience_buffer)>=self.buffer_threshold:
            self.train_ppo()
        return assignments
