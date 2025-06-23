
Autonomous Urban Recycler (AURo)
Team AURoTech
Team Members
● Garvit Singhal
● Krishiv Gupta
● Aryendra Singh Rathore

Team Presentation
● I’m Garvit Singhal , a 15 ‑year‑old high‑school student based in Jaipur,
India. I have a deep passion for all areas of technology, especially
anything that can benefit society through IoT , AI , and Machine Learning.
● My role in this project: I developed the software & designed the LLM
algorithm.
● I’m Krishiv Gupta , a 15 ‑year‑old student in Class 10 at Cambridge Court
World School. I’m a diligent learner, passionate about contributing to our
project. I’m excited to collaborate with the team and committed to
delivering quality work.
● My role in this project: I created the hardware and navigation,&
adjusted the software accordingly.
● I’m Aryendra Singh Rathore , a 15-year-old aspiring student from
Cambridge Court World School and a passionate robotics
enthusiast. I’m eager to explore new horizons and make meaningful
contributions through innovative projects.
● I am responsible for PPT, Presentation, & Research work.
Submitted on {TBD}.

Introduction:.............................................................................................................................
Robotic Solution Overview:....................................................................................................
Project Initiation:.....................................................................................................................
Hardware Development:..........................................................................................................
Software Development:...........................................................................................................
Evaluation and Optimisation:.................................................................................................
Design and Methodology of Mechanical Construction:.......................................................
Waste Classification Pipeline:..............................................................................................
Coding of the Solution:.........................................................................................................
Microcontroller:.......................................................................................................................
Arduino Mega (Main Controller):............................................................................................
ESP32-CAM (Vision and LLM):..............................................................................................
ESP8266 (Smart Bin Communication):.................................................................................
LLM/AI Integration (via API):..................................................................................................
Cost Estimation:..................................................................................................................
Business Preview................................................................................................................
Market Opportunity................................................................................................................
Target Customers..................................................................................................................
Business Model.....................................................................................................................
Scalability...............................................................................................................................
Revenue Streams..................................................................................................................
Competitive Advantage..........................................................................................................
Challenges Faced During the Development Process.......................................................
Integration of Hardware and Software...........................................................................
Real-Time Data Transmission............................................................................................
Algorithm Optimization.......................................................................................................
Environmental and Real-World Factors.............................................................................
Social Impact & Innovation.................................................................................................
Cleaner Cities, Healthier Communities............................................................................
Revolutionising Waste Management...............................................................................
Empowering Municipal Services......................................................................................
LLM-Driven Approach......................................................................................................
Collaboration and Importance................................................................................................
Municipal Corporations and Urban Planners...................................................................
Citizens and Local Communities......................................................................................
Concrete Example of Application...........................................................................................
Websites:...............................................................................................................................
1. Introduction:.............................................................................................................................
● Project Overview:
This project presents an automated four-wheel mobile robot designed to enhance
urban waste management. Equipped with a 4-axis robotic arm and six internal
compartments, the robot autonomously services smart dustbins, collecting and
segregating waste using sensor and vision-based classification techniques.
● Problem Statement:
In Indian cities, 30–40% of waste, approximately 18.6 to 24.8 million tons annually , is
either not collected or ends up scattered on streets due to:
● Poor waste collection systems
● Irregular disposal practices
● Lack of public awareness
Uncollected waste clogs drains and leads to stagnant water , which can cause serious
public health issues such as dengue, malaria, and cholera.
● Solution:
The proposed solution uses an autonomous robotic system that:
● Navigates urban environments
● Communicates with smart dustbins via ESP modules
● Uses Arduino Mega and ESP32-CAM for control and processing
● Performs real-time waste collection and sorting using vision and sensors
● Organises waste into six categorised compartments
This system ensures source-level segregation and automated pickup, significantly
improving waste management efficiency.
● Benefits:
● Minimises manual labour and exposure to hazardous waste
● Improves segregation accuracy, leading to higher recycling rates
● Helps prevent disease outbreaks by reducing street litter
● Lowers operational costs for municipalities over time
● Supports a cleaner urban environment
● Efficiency:
The robot provides:
● Timely and consistent waste collection
● Autonomous navigation and decision-making
● Precise waste classification using advanced sensors and vision
● Reliable communication between bins and the robot for optimized
performance
● Real-Life Application:
Ideal for deployment in:
● Urban municipal zones
● Smart city initiatives
● Gated communities and residential complexes
● Commercial and industrial campuses
2. Robotic Solution Overview:....................................................................................................
This project is a completely self ‑ sufficient, connected waste ‑ separation system
aimed at optimising city refuse collection and recycling. Fitted with a four ‑ wheeled
differential ‑ drive chassis and a four ‑ axis manipulator arm , the robot utilises an
ESP32 ‑ CAM ‑ mounted end effector for real ‑ time visual identification of single waste
items, while built ‑ in ultrasonic sensors enable 360° obstacle evasion. Upon getting
“bin full” notifications through MQTT from smart city trash bins (each equipped with
an ESP8266 and ultrasonic level sensor ), the robot moves to the designated spot
using waypoint navigation and wheel ‑ encoder–aided odometry. It triggers the bin’s
release system , vibrates its tray to settle contents, and carries out a multi ‑ step
sorting process : moisture detection guides damp waste to the wet waste section ; a
specialised metal detector identifies metal objects; and a lightweight vision
algorithm sorts paper, glass, and plastics into their designated bins, while any
unidentified items are redirected to another compartment. All subsystems— sensor
integration , actuator management , and decision ‑ making logic —are coordinated by
an Arduino Mega , while advanced monitoring , diagnostics , and route planning are
supported through cloud ‑ based LLM APIs , allowing for natural ‑ language updates and
adaptable task scheduling. This coordinated method not only automates the
complete waste ‑ collection process but also generates detailed telemetry for
effective recycling operations.
3. Project Initiation:.....................................................................................................................
● Define project objectives, scope, and deliverables.
● Establish project team roles and responsibilities.
● Set up project management tools and communication channels.
Research and Requirements Gathering:
● Conduct a comprehensive review of existing Waste collection and sorting technologies
and systems.
● Gather requirements from stakeholders, including end-users, researchers, and
emergency responders.
● Identify technical specifications and performance criteria for the robotic solution.
Conceptual Design:
● Develop conceptual design of the robotic solution, including:
● Overall architecture and system components.
● Sensor configurations and placement.
● Mobility and navigation mechanisms.

● Create conceptual drawings and schematics to visualise the design.
4. Hardware Development:..........................................................................................................
Procure or develop necessary hardware components, including:

Chassis & Mobility
● Four‑wheeled differential‑drive chassis frame
● 4 × DC geared motors
● 4 × Wheel encoders
● Motor driver shield L298N
Manipulation
● Four‑axis manipulator arm servo-based
● High‑torque servos
● Vibration motor
Sensing & Vision
● ESP32‑CAM module (object recognition)
● 8 × Ultrasonic range sensors (for 360° obstacle detection)
● Ultrasonic level sensor (in each smart bin)
● Moisture sensor
● Metal detection module
● VL53L1X (Depth analysis)
Computation & Control
● Arduino Mega 2560 (central coordination)
● ESP8266 (MQTT gateway for smart bins)
● ESP32 Cam,(Navigation and LLM segmentation)

Power & Electrical
● Rechargeable Li‑ion or LiFePO₄ battery pack
● DC–DC converters/voltage regulators

Communications
● Wi‑Fi modules (ESP32/ESP8266)
● MQTT broker (cloud)

5. Software Development:...........................................................................................................
● Program a microcontroller for sensor data acquisition and processing.
● Develop code for image capture and transmission using the ESP32 Cam module.
● Create scripts for LLM to recognise trash and use a Single point ToF sensor and an
Camera to calculate the angle to take the arm to the trash.

The camera and ToF sensor are mounted at a known fixed distance apart (say h), and
the ToF sensor measures the distance d from the sensor to the trash object. Assuming a
flat ground, we can compute the angle θ from the arm base to the trash using basic
trigonometry:
θ=𝑡𝑎𝑛−^1 (ℎ/𝑑)
Where:

● θ is the angle between the arm and the trash object (in radians or degrees),
● h is the vertical or horizontal offset between the camera and the ToF sensor,
● d is the direct distance to the trash from the ToF sensor.
This angle is used to rotate the robotic arm to align with the trash for pickup

import math
h = 10 # Fixed Distance between ToF sensor and camera
d = get_distance_from_tof_sensor()
theta_rad = math.atan(h / d)
theta_deg = math.degrees(theta_rad)
print(f"Angle to trash: {theta_deg:.2f}°")
This approach combines AI-based vision for detection with geometric reasoning for precise
robotic manipulation — all while using low-cost sensors.

● Make the Sorting algorithm using the sensors and ESP32-Cam
● Test software components individually and in conjunction with hardware.
Integration and Testing:
● Integrate hardware and software components to create a functional prototype of the
robotic solution.
● Conduct rigorous testing to evaluate performance and reliability:
● Test sensor accuracy and responsiveness in simulated and real-world conditions.
● Assess data transmission and communication capabilities.
● Iterate on design and implementation based on test results and feedback.
Documentation and Training:
● Document the robotic solution's design specifications, technical details, and user
manuals.
● Develop training materials and conduct training sessions for end-users and maintenance
personnel.
● Ensure comprehensive documentation of the development process for future reference
and knowledge transfer.
Deployment and Field Testing:
● Deploy the robotic solution in an actual City or a landfill.
● Monitor system performance and collect data on its effectiveness in clearing the
area.
● Gather feedback from end-users and stakeholders to identify areas for
improvement and optimisation.

6. Evaluation and Optimisation:.................................................................................................
● Evaluate field test results and performance metrics against project objectives and
requirements.
● Identify and address any issues or shortcomings through software updates, hardware
modifications, or system enhancements.
● Based on feedback and lessons learned, optimise the robotic solution for improved
accuracy, reliability, and usability.
Scaling and Expansion Plans :
● Explore opportunities for scaling and expanding the robotic solution to additional regions
or applications.
● Consider potential partnerships or collaborations for further development and
deployment.
● Continuously monitor advancements in technology and research for future
enhancements and upgrades.

7. Design and Methodology of Mechanical Construction:.......................................................
The mechanical construction of AURo integrates various sensors and components within a
robust framework to ensure accurate monitoring of soil parameters and effective communication
of warning alerts. Here's a breakdown of the design and methodology:

Structural Framework:
● The AURo system is built on a rugged four-wheel mobile platform designed to
operate on urban terrain.
● It houses a 4-axis robotic arm and six internal compartments for effective waste
segregation. The chassis and enclosure are durable and weather-resistant , protecting
onboard electronics from environmental exposure.
● The robot includes mounting points for sensors and cameras to ensure optimal data
collection and object detection.
Sensor Integration:

● ESP32-CAM for visual waste detection and guidance of the robotic arm
● Soil moisture sensor to differentiate between wet and dry waste
● Metal detection circuit (open circuit) for identifying metallic waste
● Ultrasonic sensors (4 directions) for obstacle avoidance and navigation
● ToF sensors for proximity and alignment
● Load cells (future integration) to measure compartment capacity
Microcontroller and Data Processing:

● An Arduino Mega serves as the primary controller, coordinating the movement of the 4
servo motors on the robotic arm, the motor driver for the wheels, and all sensor inputs.
● Data from the ESP32-CAM , moisture sensor , and metal detector is processed to
guide the arm's actions. The robot uses logic-based sequencing to determine waste
type and deposit it in the correct compartment.
● Large Language Models (LLMs) and AI assist in higher-level decision-making,
communication.
Communication Modules:
● Each dustbin has an ESP8266 module that sends status updates to the robot’s ESP
when full. The robot then autonomously navigates to the bin, guided by GPS, ultrasonic
data , and camera vision. Bin location and status are logged and used for routing
decisions. The system can also be switched to RF in future versions using NRF24L01.
Administrative Interface:

● Real-time robot location and status
● Smart bin status (empty/full)
● Maps integration to show the positions of bins and the robot
● Control options and logs for waste management activities
Autonomous Navigation:

● Ultrasonic Sensors (4-directional):
Detect obstacles and enable safe manoeuvring in city environments.
● Camera (ESP32-CAM):
Provides real-time visual feedback to assist in object recognition, bin alignment, and
path verification.
● Predefined Pathways or Coordinates:
If the city layout is mapped, the robot can use pre-programmed paths or bin
coordinates to optimise movement.
8. Waste Classification Pipeline:..............................................................................................
Each piece of waste is evaluated through a multi-step AI-driven pipeline :

Visual Detection:
The ESP32-CAM locates a piece of trash on the tray.
Moisture Check:
The robotic arm brings the moisture sensor close to the object:
○ If wet , it goes to the wet waste compartment.
Metal Detection:
The object is passed over the open circuit metal detector :
○ If metal , it is placed in the metal compartment.
AI-Based Material Classification (Camera + LLM):
If neither wet nor metal:
○ The camera checks shape, color, and texture.
○ LLM/AI model classifies it as paper , glass , plastic , or others.
Final Placement:
The object is dropped into the relevant compartment. If no criteria match, it's sent to the
‘others’ compartment.
9. Coding of the Solution:.........................................................................................................
The coding of the Autonomous Urban Robotic Waste Segregator (AURo) involves
programming the Arduino Mega, ESP32-CAM, and ESP8266 modules for sensor
interfacing, AI-based waste classification, navigation, and wireless communication.
Here's a breakdown:

Microcontroller:.......................................................................................................................
Arduino Mega (Main Controller):............................................................................................
● Sensor Interface:
Code will acquire input from:
○ Ultrasonic sensors (4 directions for navigation)
○ Soil moisture sensor
○ Open circuit metal detector
● Motor & Servo Control:
The Arduino will control:
○ Motor driver for wheel movement
○ 4 servo motors for the robotic arm's joints
● Decision Logic:
Code will:
○ Perform sensor value checks (moisture and metal)
○ Route trash to the appropriate compartments
○ Send signals to actuate arm movements based on object classification
● Communication:
It will handle serial communication with the ESP32-CAM and ESP8266 , ensuring
coordination between modules.
ESP32-CAM (Vision and LLM):..............................................................................................
● Camera Operations:
Programmed to:
○ Capture images of trash on the tray
○ Stream or transmit frames for analysis
● Object Classification:
Using pretrained models or interfaced LLMs to:
○ Detect paper, glass, plastic , or classify them into others
○ Guide the robotic arm to correct pick-up and drop points
● Feedback to Arduino:
The classification result is sent to Arduino via serial commands , initiating the sorting
procedure.
ESP8266 (Smart Bin Communication):.................................................................................
● Dustbin Status Detection:
Continuously reads the ultrasonic sensor to detect when the bin is full.
● Wireless Transmission:
Sends a bin-full alert and location ID to the robot's ESP32 using ESP-NOW protocol.
● RF can be used in the future.
LLM/AI Integration (via API):..................................................................................................
● Classification Server/API:
○ Hosted on the cloud
○ Receives the image from ESP32-CAM
○ Uses an AI model, Gemini 2.5 flash to classify the item
○ Returns a JSON with the predicted waste type
● Model Logic:
○ Trash is classified as wet , metal , paper , plastic , glass , or other
10. Cost Estimation:..................................................................................................................
Component/Module Quantity Unit Cost (₹) Total Cost (₹)
Arduino Mega 1 850 850
ESP32-CAM 1 600 600
ToF Sensor (VL53L0X) 1 250 250
Ultrasonic Sensors (HC-SR04) 4 80 320
Motor Driver (L298N) 1 150 150
DC Motors with Wheels 4 300 1200
Robotic Arm (4-DOF) 1 1800 1800
Servo Motors (for arm) 4 180 720
Battery Pack (12V/9V) 1 900 900
ESP8266 for Smart Dustbins 1 250 250
Mini Vibration Motor 6 50 300
Ultrasonic Sensors for Bins 1 80 80
Metal Sensor Module 1 350 350
Soil/Moisture Sensor 1 200 200
Chassis & Frame (metal/plastic) 1 1000 1000
Misc (wires, PCB, nuts, etc.) – – 500
11. Business Preview................................................................................................................
Market Opportunity................................................................................................................
India alone generates over 62 million tonnes of waste annually. Urban centers are under
increasing pressure to manage waste more effectively and sustainably. Municipalities are
actively seeking smart city technologies to improve cleanliness, efficiency, and resource
management.

AURo directly addresses:

● Labour shortages in waste collection.
● Delayed pickups due to manual scheduling.
● Improper segregation leads to pollution and landfill overflow.
Target Customers..................................................................................................................
● Municipal Corporations (Tier 1 & Tier 2 cities).
● Private Waste Management Contractors.
● Smart City Projects under the Government of India initiatives.
● Large housing societies, townships, and campuses.
Business Model.....................................................................................................................
B2G (Business to Government): Offer AURo as a deployable system to urban local
bodies.
B2B (Business to Business): Collaborate with facility management companies,
hospitals, and IT parks for localised deployment.
Scalability...............................................................................................................................
The modular nature of the system allows for:

● Adding multiple smart bins to any city layout.
● Deploying more AURo units for different zones.
● Integrating cloud-based analytics for performance and waste generation trends.
Revenue Streams..................................................................................................................
● Sale of AURo Units: One-time cost + optional annual maintenance.
● Subscription for Smart Bin Software & Monitoring.
● Custom Integrations for specific industrial or environmental use cases.
Competitive Advantage..........................................................................................................
● Combines AI-driven waste classification, autonomous mobility, and IoT-enabled
bins—unlike most current semi-manual solutions.
● Lower cost of deployment compared to existing industrial robotic solutions.
● High adaptability to Indian urban infrastructure.
12. Challenges Faced During the Development Process.......................................................
1. Integration of Hardware and Software...........................................................................
● Ensuring seamless coordination between sensors, motors, and actuators with
software logic on the Arduino Mega and ESP32-CAM was complex.
● Frequent hardware-software interface bugs required rigorous debugging and testing.
● Synchronising arm control with classification results demanded precise timing and
multi-device communication.
2. Real-Time Data Transmission............................................................................................
● Establishing reliable wireless communication between the smart bins (ESP8266)
and the robot (ESP32) in urban conditions was difficult.
● Packet loss, latency, and Wi-Fi interference in populated areas affected performance.
● Ensuring real-time coordination with limited bandwidth was a key hurdle.
3. Algorithm Optimization.......................................................................................................
● Running image classification and sorting logic on limited microcontroller
resources posed computational constraints.
● Balancing processing speed, accuracy, and power consumption required
fine-tuning algorithms.
● Efficiently handling parallel tasks like movement, sorting, and communication was
essential but challenging.
5. Environmental and Real-World Factors.............................................................................
● Variability in lighting conditions, outdoor temperature, and trash surface wetness
impacted sensor accuracy and camera reliability.
● Dust, water, and vibrations affected the mechanical performance of components.
● Designing a robust enclosure and durable mechanisms was essential to ensure
long-term operation in public spaces.
13. Social Impact & Innovation.................................................................................................
Cleaner Cities, Healthier Communities............................................................................
● AURo directly addresses the issue of uncollected and mismanaged waste , which
leads to pollution, disease outbreaks , and clogged urban infrastructure.
● By automating waste segregation and collection , AURo helps keep streets clean ,
reducing the risks of diseases like dengue, malaria , and cholera caused by waste
accumulation and stagnant water.
Revolutionising Waste Management...............................................................................
● With onboard classification systems and segregated compartments , AURo sorts
trash into wet, metal, plastic, glass, paper , and others, drastically improving recycling
efficiency.
● Reduces dependency on manual labour in waste sorting, minimising human exposure
to hazardous waste.-
Empowering Municipal Services......................................................................................
● Robots can work 24/7 , enabling more frequent and precise waste collection, even in
remote or congested areas.
LLM-Driven Approach......................................................................................................
● Integration with Large Language Models (LLMs) enables intelligent decision-making ,
communication with servers, and adaptability to dynamic environments.
Collaboration and Importance................................................................................................
Municipal Corporations and Urban Planners...................................................................
● Essential for deploying AURo across city zones, setting up smart dustbins , and
mapping waste hotspots.
● Collaboration ensures policy alignment , infrastructure compatibility, and long-term
adoption.
Citizens and Local Communities......................................................................................
● Encouraging citizens to use smart bins correctly and engage with clean city
initiatives increases system effectiveness.
● Promotes eco-conscious behaviour , community responsibility , and public support.
Concrete Example of Application...........................................................................................
Scenario : A mid-sized city like Jaipur integrates AURo with its smart waste
management infrastructure.
● Who Would Use It :
Municipal cleaning departments , urban planning authorities , and AI-driven fleet
management systems.
● Beneficiaries :
City residents , particularly in high-density urban zones, where waste
mismanagement is a daily problem.
● Impact :
AURo ensures timely pickup , on-the-spot segregation , and eco-friendly processing
leading to cleaner streets , healthier air , and increased recycling rates , while also
saving public funds.
List of Sources:
Websites:...............................................................................................................................
● https://www.researchgate.net/publication/350437509_Intelligent_Waste_Management_S
ystem_Using_Artificial_Intelligence
● https://ieeexplore.ieee.org/document/
● https://en.wikipedia.org/wiki/Waste_separation
● https://swachhbharatmission.gov.in/
People: Manpreet Kaur(Robotics teacher at CCWS) & Nisha Sharma(HOD of Science at
CCWS)