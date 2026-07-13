source /opt/ros/jazzy/setup.sh

export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
[ -t 0 ] && export ROS_SUPER_CLIENT=True || export ROS_SUPER_CLIENT=False
###  Robot 4 ###
export ROS_DOMAIN_ID=0
export ROS_DISCOVERY_SERVER="10.5.113.104:11811;"

ros2 service call /robot4/robot_power irobot_create_msgs/srv/RobotPower
