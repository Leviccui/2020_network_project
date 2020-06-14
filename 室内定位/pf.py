import numpy as np
from numpy.random import uniform, randn, random, seed
from filterpy.monte_carlo import multinomial_resample
import scipy.stats

x_outer=[6.15,38]
x_inner=[10,33]
y_outer=[4.5,22.59]
y_inner=[10,18]


def create_particles(v_mean,v_std,n_particles):
    ###粒子状态设置为(坐标x，坐标y，运动方向，运动速度)
    ###将场地模拟成长方形内嵌长方形的环状

    count=0
    np.random.seed(1234)
    temp=[]
    particles = np.empty((n_particles, 4))
    
    while count<n_particles:
        x=x_outer[0]+(x_outer[1]-x_outer[0])*np.random.rand()
        y=y_outer[0]+(y_outer[1]-y_outer[0])*np.random.rand()
        if(x_inner[0]<x<x_inner[1] and y_inner[0]<y<y_inner[1]):
            continue

        heading=np.random.rand()* 2 * np.pi
        v=v_mean + np.random.rand() * v_std
        temp.append([x,y,heading,v])
        count+=1

    return np.array(temp)
    '''
    particles = np.empty((n_particles, 4))
    particles[:, 0] = uniform(x_outer[0], x_outer[1], size=n_particles)
    particles[:, 1] = uniform(y_outer[0], y_outer[1], size=n_particles)
    particles[:, 2] = uniform(0, 2 * np.pi, size=n_particles)
    particles[:, 3] = v_mean + (randn(n_particles) * v_std)
    '''
    '''
    temp_list=particles.
    for p in range temp:
        if(x_inner[0]<p[0] and p[0]<x_inner[1] and y_inner[0]<p[1] and p[1]<y_inner[1])
            continue
    '''

    return particles

def predict_particles(particles, std_heading, std_v):
    #这里的预测规则设置为：粒子根据各自的速度和方向（加噪声）进行运动，如果超出边界则随机改变方向再次尝试，"""
    idx = np.array([True] * len(particles))
    particles_last = np.copy(particles)

    for i in range(100): # 最多尝试100次
        if i == 0:
            particles[idx, 2] = particles_last[idx, 2] + (randn(np.sum(idx)) * std_heading)
        else:
            particles[idx, 2] = uniform(0, 2 * np.pi, size=np.sum(idx)) # 随机改变方向
        particles[idx, 3] = particles_last[idx, 3] + (randn(np.sum(idx)) * std_v)
        particles[idx, 0] = particles_last[idx, 0] + np.cos(particles[idx, 2] ) * particles[idx, 3]
        particles[idx, 1] = particles_last[idx, 1] + np.sin(particles[idx, 2] ) * particles[idx, 3]
       
        # 判断超出边界的粒子
        idx = ((particles[:, 0] < x_outer[0])
                | (particles[:, 0] > x_outer[1])
                | (particles[:, 1] < y_outer[0]) 
                | (particles[:, 1] > y_outer[1])
                | ((x_inner[0]<particles[:, 0]) & (particles[:, 0]<x_inner[1]) & (y_inner[0]<particles[:, 1]) & (particles[:, 1]<y_inner[1])))
        if np.sum(idx) == 0:
            break

def update_particles(particles, weights, pos, d_std):
    ###粒子更新，根据观测结果中得到的位置pdf信息来更新权重，这里简单地假设是真实位置到观测位置的距离为高斯分布
    # weights.fill(1.)
    distances = np.linalg.norm(particles[:, 0:2] - pos, axis=1)
    weights *= scipy.stats.norm(0, d_std).pdf(distances)
    weights += 1.e-300
    weights /= sum(weights)

def neff(weights):
    ###判断当前要不要进行重采样
    return 1. / np.sum(np.square(weights))

def resample_from_index(particles, weights, indexes):
   ###根据指定的样本进行重采样
    particles[:] = particles[indexes]
    weights[:] = weights[indexes]
    weights /= np.sum(weights)

def estimate(particles, weights):
    """估计位置"""
    return np.average(particles, weights=weights, axis=0)

def run_pf(particles,weights,pos):
    std_heading=0.5
    std_v=10
    predict_particles(particles, std_heading, std_v) # 1. 预测
    update_particles(particles, weights, pos, 4) # 2. 更新
    if neff(weights) < len(particles) / 2: # 3. 重采样
        indexes = multinomial_resample(weights)
        resample_from_index(particles, weights, indexes)
    return estimate(particles, weights) # 4. 状态估计