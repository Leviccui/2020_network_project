﻿# 2020_network_project


### 1. web接口  
  
	index.html: 网页html文件。  
	my_db.js：网页所需的query函数和一些辅助函数。  
	jquery-3.5.0.min.js: jquery文件。  
  
	测试运行，需要解决跨域问题：  
		windows>npm install -g local-cors-proxy  
		windows>lcp --proxyUrl http://101.200.169.212:8080  

### 2. 室内定位  
  
	main.py: 主程序。  
	locate2and3points.py: 测距、两点定位、三角几何定位。  
	pf.py：粒子滤波算法。  
	2020-04-07-Abeacon3.xlsx：输入，主要为不同时间距离各个ap的rssi值。  
	2020-04-07-15个测试位置.xlsx：输入，主要为人工测的15个位置。  
	2020-04-07-Abeacon3_result.xls： 输出，包括x坐标，y坐标，时间。  
	  
	测试运行需要安装filterpy和scipy(粒子滤波需要)	  
  
	目前运行的算法是两点定位+三角几何定位+粒子滤波。  
	运行输出的图示：	红色：标准轨迹 	蓝色：两点定位+三角几何定位预测轨迹 	绿色：两点定位+三角几何定位+粒子滤波预测轨迹。  
	运行文字输出：13个点的距离误差。  
	如果想输出不经过粒子滤波的结果，可以将main.py的161行results=tri_pf_predictions改为results=tri_predictions。  
	如果不想使用三角几何定位，而想用纯三角定位(极大似然估计法），可以将locate2and3points.py中的three_point注释部分解除注释，但该方法效果不好，不建议使用。  














