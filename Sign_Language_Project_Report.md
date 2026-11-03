# Real-time Arabic Sign Language Recognition System using MediaPipe and Raspberry Pi

**A project Submitted To Council of the College of Computer Science & Information Technology, Information Systems Department, University of Al Qadisiyah in Partial Fulfilment of the Requirements for the BSc Degree in Information Systems**

**By:**
**Mohammed Ali Kifah**

**Supervised By:**
**Qusay Omran**

**April 2025**

---

## Abstract (English)
Sign language is the primary means of communication for the deaf and hard-of-hearing community. However, the lack of understanding of sign language among the general public creates a significant communication barrier. This project aims to bridge this gap by developing a real-time Arabic Sign Language (ArSL) recognition system using the Raspberry Pi platform. The proposed system utilizes Google’s MediaPipe framework for accurate hand landmark detection and a custom-trained machine learning model for gesture classification. The implementation covers the entire process from hardware setup, data collection, and model training to the development of a user-friendly web interface that converts hand gestures into Arabic text and speech. The results demonstrate that the system is efficient, portable, and capable of operating in real-time with high accuracy, providing a foundation for low-cost assistive technologies for the deaf community in Iraq.

## المستخلص (العربية)
تُعد لغة الإشارة الوسيلة الأساسية للتواصل بين أفراد مجتمع الصم وضعاف السمع، إلا أن نقص المعرفة بهذه اللغة لدى عامة الناس يؤدي إلى فجوة تواصل كبيرة. يهدف هذا المشروع إلى ردم هذه الفجوة من خلال تطوير نظام فوري للتعرف على لغة الإشارة العربية (ArSL) باستخدام منصة Raspberry Pi. يعتمد النظام المقترح على إطار عمل Google MediaPipe للاكتشاف الدقيق لنقاط معالم اليد، ونموذج تعلم آلي تم تدريبه خصيصاً لتصنيف الإيماءات. تشمل عملية التنفيذ كافة المراحل بدءاً من إعداد المكونات المادية، وجمع البيانات، وتدريب النموذج، وصولاً إلى تطوير واجهة ويب سهلة الاستخدام تقوم بتحويل إشارات اليد إلى نصوص ومقاطع صوتية باللغة العربية. أظهرت النتائج أن النظام يتميز بالكفاءة والقابلية للنقل والقدرة على العمل في الوقت الفعلي بدقة عالية، مما يوفر أساساً لتقنيات مساعدة منخفضة التكلفة لمجتمع الصم في العراق.

---

## Chapter One: Introduction

### 1.1 Overview
Communication is an essential element in our daily life. A lack of communication can lead to disappointment, isolation, and dissatisfaction. For deaf people, sign language is an essential way to communicate and interact with others. When two people master sign language, they can communicate effectively using gestures and expressions. However, for communication to be successful, both parties must be able to understand the sign language used in their region or country. Sign language allows deaf people to express their thoughts and opinions freely; therefore, it plays a vital role in integrating this group into society and enabling them to participate fully in daily life.

Manual movements and gestures form the main basis of this language. It is especially important for people with hearing disabilities as it is the primary means of communication. Human action recognition has become an increasingly popular field in pattern recognition and computer vision. Hand gesture recognition has become one of the effective ways of human-computer communication, offering more flexibility compared to traditional methods.

### 1.2 Research Problem
There are three main challenges in using computer vision to interpret sign language that this research addresses:
1.  **Variable Ambient Lighting:** Systems may not perform well under inappropriate lighting conditions, affecting the visual sensor's clarity.
2.  **Diversity of Sign Languages:** Variations between regions and individuals represent a major challenge for machine learning model generalization.
3.  **Complex Physical Movements:** Recognizing complex and precise movements is difficult due to their variable nature and speed.

### 1.3 Related Works
This project builds upon significant research in the field of hand gesture detection and assistive technology. The following studies provided crucial foundations:

*   **Rangkuti et al. (2023) [1]:** Optimized hand gesture recognition on **Raspberry Pi 4**, evaluating CNN models like YOLOv3-Tiny and YOLO-Fastest. Their work highlighted the importance of balancing FPS and accuracy for real-time interaction.
*   **Hobbs & Ali (2025) [2]:** Developed a **Raspberry Pi 5** based system for smart home control using **MediaPipe** for hand landmark normalization, reaching 20.4 FPS and proving the efficiency of modern edge hardware.
*   **Abini et al. (2024) [3]:** Proposed a comprehensive deep learning system using **Raspberry Pi 3** and **MobileNet-V2**, achieving 99.52% accuracy. This study strongly advocated for multi-modal output (text and speech).
*   **Anusha & Jyothi (2022) [4]:** Created an AI-based speaking system using **Raspberry Pi** and **OpenCV**, demonstrating that vision-based systems are superior to older sensor-based gloves for deaf-mute communication.
*   **Mozarkar et al. (2025) [5]:** Investigated gesture-controlled electrical appliances, providing insights into the future of hands-free interaction and the impact of environmental noise on gesture accuracy.

### 1.4 Aim and Objective of the Thesis
**The Aim:** To develop an intelligent, portable, and real-time translation system for the full Arabic Sign Language alphabet (28 letters) using the Raspberry Pi.

**The Objectives:**
1.  To implement a robust 21-point hand landmark extraction system using **MediaPipe**.
2.  To train an optimized **Keypoint Classifier** for all 28 Arabic letters with high accuracy.
3.  To deploy the system as a **Flask Web Application** for easy accessibility from any device.
4.  To bridge the communication gap by integrating **Microsoft Edge-TTS** for Arabic speech output.

### 1.5 Thesis Contribution
The main contributions of this study are:
1.  **Full ArSL Alphabet Coverage:** Unlike studies focusing on small subsets, this project collects data and trains a custom model for the complete set of **28 Arabic characters**.
2.  **Edge-Device Implementation:** Successfully deploying a stable AI pipeline on the **Raspberry Pi 4**, proving that real-time translation is possible on low-cost hardware.
3.  **Cross-Platform Web Interface:** Transitioning from a local script to a full-stack Flask application, allowing interaction via smartphones and tablets on the same network.

### 1.6 Thesis Organization
The remainder of this thesis is organized as follows:
*   **Chapter 2:** Background for Project, covering programming languages, libraries, and hardware.
*   **Chapter 3:** Proposed Model and Methodology, including dataset and system diagrams.
*   **Chapter 4:** Experimental Results and Discussion.
*   **Chapter 5:** Conclusions and Future Research.

### 1.7 References for Chapter One
[1] Abdul Haris Rangkuti et al., "Optimizing Hand Gesture Recognition Using CNN Model Supported by Raspberry pi for Self-Service Technology," *International Journal on Informatics Visualization*, 2023.
[2] Thomas Hobbs and Anwar Ali, "Smart Home Control Using Real-Time Hand Gesture Recognition and Artificial Intelligence on Raspberry Pi 5," *Electronics*, 2025.
[3] Abini M.A et al., "A Comprehensive Deep Learning Based System for Real Time Sign Language Recognition and Translation Using Raspberry Pi," *International Journal of Computer Trends and Technology*, 2024.
[4] Chilupuri Anusha and N Krishna Jyothi, "AN ARTIFICIAL INTELLIGENCE-BASED SPEAKING SYSTEM FOR DUMB PEOPLE," *International Journal of Engineering Applied Sciences and Technology*, 2022.
[5] Aditi Mozarkar et al., "Hand Gesture Controlled Electrical Appliance," *International Journal on Science and Technology (IJSAT)*, 2025.

---

# **Chapter Two: Background for Project**

### 2.1 Introduction
This chapter provides the theoretical and technical foundation of the project. It explores the global landscape of sign language, the specific importance of focusing on Arabic Sign Language within our region, and a detailed examination of the hardware and software stack—led by the Raspberry Pi platform—that makes real-time, portable translation possible.

### 2.2 Sign Language: A Global and Regional Perspective
#### 2.2.1 The Multiplicity of Sign Languages
One of the most significant insights in modern socio-linguistics is the recognition that sign languages are not mere visual mirrors of spoken languages, nor are they a single, unified global method of communication. Contrary to common misconceptions, there is no single universal sign language. Just as spoken languages like Arabic, English, and Mandarin evolved independently within distinct cultural contexts, sign languages possess their own autonomous grammars, syntax, and cultural idioms.

Globally, the World Federation of the Deaf recognizes over 300 distinct sign languages [18]. Key examples include:
*   **American Sign Language (ASL):** Predominantly used in the United States and parts of Canada, ASL is a complete, grammatically complex visual language. Many people are surprised to learn that it is more closely related to French Sign Language than to British Sign Language.
*   **British Sign Language (BSL):** Used in the United Kingdom, BSL is distinctively known for its use of a two-handed manual alphabet for spelling (fingerspelling), whereas ASL and many others use a single-handed alphabet.
*   **Indo-Pakistani Sign Language (IPSL):** A regional language with millions of users across the Indian subcontinent. It features unique cultural gestures and has various local dialects that reflect the linguistic diversity of the region.
*   **Arabic Sign Language (ArSL):** Despite the unified spoken Arabic script, Arabic sign languages vary significantly between countries (e.g., Egyptian vs. Levantine vs. Gulf sign languages). However, efforts are ongoing to standardize a unified version for educational and official broadcast contexts, which forms the basis for the gestures modeled in this project.

The complexity of these languages lies in their multi-layered structure:
*   **Manual Components:** These involve specific hand shapes, orientations (the direction of the palm), and locations (where in space the sign is performed).
*   **Non-Manual Signals:** Facial expressions, eye movements, and body posture are integral to the grammar, often acting as "adverbs" or "adjectives" that change the meaning of a hand gesture.
*   **Static vs. Dynamic Signs:** Some signs are static postures (like the alphabet letters captured in this project), while others are dynamic movements through space time.

This diversity means that a "handwave" or a specific finger configuration can have entirely different meanings—or no meaning at all—when moving from one linguistic region to another. Understanding this global variety is essential for developing AI systems, as a model trained on one language cannot simply be "translated" to another without retraining on new, culturally specific data.

#### 2.2.2 The Choice of Arabic Sign Language (ArSL)
The decision to focus specifically on **Arabic Sign Language (ArSL)** is driven by both social necessity and regional proximity. Living in Iraq and being part of the Arabic-speaking world, I identified a critical "Translation Gap" where local deaf individuals often struggle to find accessible real-time interpretative tools tailored to our specific dialect and culture. By choosing ArSL, I aim to provide a practical solution that empowers my local community and ensures that technology serves those in my immediate environment.
### 2.3 Hardware Infrastructure: The Raspberry Pi Ecosystem
The central computing unit of this project is the **Raspberry Pi**, a credit-card-sized Single Board Computer (SBC). Its role in this research is not merely as a processor, but as an enabling platform for "Edge AI"—bringing complex neural network inference out of the cloud and into a portable, standalone device.

#### 2.3.1 Technical Architecture and Rationale
The choice of the Raspberry Pi 4 Model B was informed by its **Broadcom BCM2711 SoC**, featuring a quad-core Cortex-A72 (ARM v8) 64-bit processor running at 1.5GHz. A critical technical detail is the inclusion of **NEON SIMD (Single Instruction, Multiple Data) instructions**, which are essential for accelerating the floating-point mathematics required by the MediaPipe landmark extraction engine [15]. This allows the system to process video frames efficiently without a dedicated external GPU.

As illustrated in the project’s hardware diagram (Figure 2.1), the Raspberry Pi 4 is a Credit-Card-Sized Single Board Computer (SBC) that maximizes connectivity within a minimal footprint. The physical architecture includes several key interfaces that were critical for the implementation of this real-time system:

*   **Quad-Core Processor:** The computational core of the Broadcom BCM2711, which executes the neural network inference and landmark extraction logic in real-time at 1.5GHz.
*   **High-Bandwidth USB 3.0 Ports:** (Identified by their blue inserts) These ports are essential for interfacing with high-definition optical sensors (webcams), providing the 5Gbps throughput necessary for low-latency 1080p video streaming.
*   **Standard USB 2.0 Ports:** Utilized for peripheral connectivity, such as keyboards and pointing devices, during the development and calibration phases of the system.
*   **Dual Micro-HDMI Ports:** These ports allow for real-time visualization of the hand landmarks and AI classification confidence on external displays during laboratory testing.
*   **USB-C Power Management:** A modern interface providing the stable 5V/3.0A current required to sustain peak CPU workloads during continuous AI inference without power drops.
*   **Gigabit Ethernet & Wireless:** Integrated networking support (dual-band 802.11ac Wi-Fi) ensures the stability of the Flask web-server deployment, allowing the ArSL recognition interface to be accessed across local networks.
*   **CSI & GPIO Headers:** Dedicated interfaces for the Raspberry Pi Camera Module and a 40-pin header for potential future integration of tactile feedback sensors for the signer.

#### 2.3.2 Implementation Insights from Recent Research
The effectiveness of the Raspberry Pi platform for gesture recognition is well-documented in contemporary literature, proving its viability across different generations:
*   **Performance Trade-offs:** Rangkuti et al. (2023) demonstrated that the Raspberry Pi 4 is capable of running various CNN architectures (like YOLO-Fastest) for real-time store automation, but emphasized that success depends on balancing the frames-per-second (FPS) with recognition accuracy to avoid high latency [1].
*   **Generational Evolution:** While Abini et al. (2024) successfully utilized the Raspberry Pi 3 with the MobileNet-V2 model for sign translation [3], more recent studies by Hobbs & Ali (2025) suggest that the Raspberry Pi 5 provides a significant leap in performance, achieving over 20 FPS due to its upgraded CPU and RAM speeds, effectively eliminating the "stutter" often seen in older hardware during complex landmark assignments [2].
*   **Accessibility and Portability:** Research by Anusha & Jyothi (2022) and Mozarkar et al. (2025) both utilized the Pi’s small form factor to build portable assistive systems for deaf-mute communication and home automation, respectively. Highlighting that the Pi's low power consumption allows it to be powered by standard battery packs for mobile use [4][5].

#### 2.3.3 Thermal and Computational Management
Running real-time AI models on the Pi 4 environment introduces significant thermal challenges. As noted in the literature, continuous CPU utilization can lead to "Thermal Throttling," where the clock speed is reduced to protect the hardware, resulting in a sudden drop in recognition accuracy. To combat this, our implementation utilizes active PWM cooling and aluminum heatsinks, ensuring the system maintains a stable inference rate during extended operation periods [16].

### 2.4 Development Environment and Hardware
The technical development and validation of the recognition system were executed using a two-tier hardware setup, separating the training environment from the edge deployment environment.

#### 2.4.1 System Hardware Specifications
*   **Development Laptop:** 
    *   **CPU:** Intel(R) Core(TM) i5-4310U CPU @ 2.00GHz
    *   **RAM:** 8 GB DDR3
    *   **GPU:** NVIDIA GeForce GT 720M (CUDA utilized for model training) [14].
*   **Deployment Unit:** Raspberry Pi 4 Model B with 4GB/8GB RAM, supported by a 1080p Optical Sensor and active cooling systems.

For the visual acquisition component, as shown in the project hardware profile (Figure 2.2), a **Rapoo C200 HD Web Camera** was utilized. This sensor provides a 720P high-definition video stream at 30 frames per second, which is critical for providing the MediaPipe framework with clear pixel-level data for landmark extraction. The camera’s architectural design, featuring a wide-angle lens and a 360° rotation capability, allows for a broad field of view, ensuring that complex multi-hand gestures are fully captured within the frame. Its plug-and-play USB interface directly supports the Raspberry Pi’s V4L (Video4Linux) drivers, ensuring low-latency communication between the sensor and the inference engine.

### 2.5 Scientific Integrity and Software Provenance
This project maintains strict adherence to academic honesty. While an open-source codebase on **GitHub** (specifically by *bekindforurself* [17]) was used as a structural foundation, the final system is an original advancement:
1.  **Independent Dataset:** I personally collected and annotated thousands of samples for the **full 28-letter Arabic alphabet**.
2.  **Web-Migration:** I transformed the local script into a full-stack **Flask web application** for cross-platform accessibility.
3.  **Accuracy Tuning:** I independently optimized the classification layers to handle the specific linguistic nuances of ArSL.

### 2.6 References for Chapter Two
[1] Abdul Haris Rangkuti et al., "Optimizing Hand Gesture Recognition Using CNN Model Supported by Raspberry pi for Self-Service Technology," *JOIV*, 2023.
[2] Thomas Hobbs and Anwar Ali, "Smart Home Control Using Real-Time Hand Gesture Recognition and Artificial Intelligence on Raspberry Pi 5," *Electronics*, 2025.
[3] Abini M.A et al., "A Comprehensive Deep Learning Based System for Real Time Sign Language Recognition and Translation Using Raspberry Pi," *IJCTT*, 2024.
[4] Chilupuri Anusha and N Krishna Jyothi, "AN ARTIFICIAL INTELLIGENCE-BASED SPEAKING SYSTEM FOR DUMB PEOPLE," *IJEAST*, 2022.
[5] Aditi Mozarkar et al., "Hand Gesture Controlled Electrical Appliance," *IJSAT*, 2025.
[14] NVIDIA Corporation. (2024). *CUDA Programming Guide*.
[15] Broadcom Inc. (2019). *BCM2711 Datasheet*.
[16] Raspberry Pi Ltd. (2024). *Thermal management*.
[17] GitHub Repository. *Hand-tracking-first*. bekindforurself.
[18] World Federation of the Deaf. (2024). *Global Survey on Sign Languages*.

---

# **Chapter Three: Design and Implementation**

### 3.1 Introduction
The design and implementation phase represent the core engineering effort of this project. This chapter details the systematic process of transforming the conceptual framework of Arabic Sign Language (ArSL) recognition into a fully functional, real-time application. We explore the software architecture, the specific algorithms developed for prediction stability, and the aesthetic design choices that define the final "Masterpiece" interface.

### 3.2 System Architecture Overview
The system follows a modular pipeline designed for high-concurrency and low-latency execution on the Raspberry Pi 4. As illustrated in the **High-level System Architecture Diagram (Figure 3.1)**, the data flow follows a specific path through several interconnected processing stages:
1.  **Visual Acquisition:** Raw frames captured by the Rapoo C200 webcam.
2.  **Preprocessing & Landmark Extraction:** Processing frames via MediaPipe to identify 21 3D hand keypoints.
3.  **Keypoint Classification:** Mapping normalized hand geometry to one of the 28 Arabic letters.
4.  **Stability Logic Filtering:** Filtering the raw output to ensure only confident and stable signs are displayed.
5.  **Output Generation:** Rendering the result through a web UI and generating neural audio feedback.

*[Place Figure 3.1: High-level System Architecture Diagram here]*

### 3.3 Software Development Stack
Choosing the right software stack was critical for ensuring cross-platform compatibility and efficient resource management:
*   **Python v3.8+ & Virtual Environments:** Used to isolate dependencies and ensure a consistent runtime across the development laptop and the Raspberry Pi.
*   **MediaPipe v0.10.x (Tasks API):** During implementation, we faced a significant versioning challenge. We transitioned from the legacy MediaPipe solutions to the modern **Tasks API**, which provides better performance and a more robust interface for landmark detection.
*   **Flask (WSGI Server):** Selected for its lightweight nature, allowing us to build a streaming server that serves the live video feed and recognition results with minimal overhead.
*   **CSS Glassmorphism & Vanilla JS:** Used to build a premium, responsive UI without the bloat of heavy frontend frameworks.

### 3.4 Core Implementation Details

#### 3.4.1 Hand Landmark Extraction
The extraction involves mapping 21 coordinates $(x, y, z)$ for each hand detected. This was implemented using the `HandLandmarker` task. 

*[Place Figure 3.2: Screenshot of the hand landmark skeleton (21 points) being tracked in real-time here]*

#### 3.4.2 The Stability Logic Algorithm
A common issue in vision-based gesture recognition is "Flickering," where small hand tremors or environmental noise cause the model to jump rapidly between different characters. To solve this, we implemented a custom **Temporal Stability Buffer**:
*   **Logic:** A character is only "confirmed" and displayed if it appears consistently in at least 15-20 consecutive frames.
*   **Benefit:** This drastically improved the user experience, providing a "smooth" and intentional translation output.

#### 3.4.3 Integration of Arabic Text and Audio
Rendering Arabic text in computer vision applications requires specific handling due to the right-to-left (RTL) nature of the script. We utilized the **Arabic-Reshaper** and **Bidi** libraries to ensure letters are connected properly. 

As depicted in the **Arabic Text Reshaping and BiDi Rendering (Figure 3.3)**, the system performs a critical transformation to address the native RTL direction and contextual joining of Arabic letters. The figure illustrates how raw, disjointed characters are dynamically re-formed into their correct, connected visual form for presentation in the web interface. 

Furthermore, this processed text is passed to **Microsoft Edge-TTS**, allowing the system to speak the identified letter in a natural Arabic neural voice, providing immediate multi-modal feedback to the user.

### 3.5 User Interface: The "Glassmorphism" Design
To make the application feel like a professional product rather than a scientific experiment, we designed a modern interface featuring:
*   **Glow Effects:** The recognized characters appear with a neon glow that matches the UI color palette.
*   **Responsive Layout:** The design adapts to different screen sizes, allowing the device to be used on smartphones or tablets via a local network.
*   **Status Indicators:** Visual feedback indicating whether a hand is detected and the confidence level of the current prediction.

*[Place Figure 3.5: Screenshot of the final User Interface (The Masterpiece) illustrating the neon glow effect and integrated audio feedback icon]*

### 3.6 Raspberry Pi Deployment and Setup
The final phase of implementation involved configuring the Raspberry Pi environment:
1.  **OS Optimization:** Using Raspberry Pi OS (64-bit) to leverage the full capacity of the BCM2711 processor.
2.  **Environment Variable Management:** Configuring camera indices and server ports via `.env` files.
3.  **Automatic Service Setup:** Implementing a shell script (`setup_rpi.sh`) to automate the installation of OpenCV and MediaPipe dependencies.

*[Place Figure 3.6: Photo of the physical setup (Raspberry Pi, Camera, and Monitor) running the application here]*

### 3.7 System Execution Sequence (Flowchart Analysis)
To understand the implementation, it is essential to trace the operation of the system as it translates gestures in real-time. The following flowchart (Figure 3.7) illustrates the logical path from image capture to multiclass audio-visual feedback:

![Figure 3.7: System Execution Pipeline and Logical Flow](c:/Users/mohammed/ProjectStart/صوره/system_pipeline_flowchart.png)

As shown in the diagram, the system operates in a continuous loop:
1.  **Frame Acquisition:** OpenCV captures high-definition frames from the webcam.
2.  **Landmark Extraction:** The MediaPipe hand-tracking module identifies if a hand is present and extracts 21 keypoints.
3.  **Data Processing:** The coordinates are normalized to ensure the system is invariant to the hand's distance from the camera.
4.  **Inference:** The TFLite engine processes the flattened landmarks to predict the character index.
5.  **Feedback:** The system renders the reshaped Arabic text on the web interface and triggers the Microsoft Edge-TTS engine for instantaneous audio confirmation.

### 3.8 Visual Data Representation: Arabic Manual Alphabet Hand Skeletons
To fulfill the requirement of showing how the model perceives gestures, this section presents the 28 Arabic letters in sign language, visualized as skeletal hand landmarks using the MediaPipe framework. Each sign below represents a specific gestational class in the model’s training set.

| Character | Hand Skeleton Gesture | Character | Hand Skeleton Gesture |
| :--- | :--- | :--- | :--- |
| **Alif (أ)** | ![Alif Skeleton](c:/Users/mohammed/ProjectStart/صوره/alif.png) | **Ba (ب)** | ![Ba Skeleton](c:/Users/mohammed/ProjectStart/صوره/ba.png) |
| **Ta (ت)** | ![Ta Skeleton](c:/Users/mohammed/ProjectStart/صوره/ta.png) | **Tha (ث)** | ![Tha Skeleton](c:/Users/mohammed/ProjectStart/صوره/tha.png) |
| **Jeem (ج)** | ![Jeem Skeleton](c:/Users/mohammed/ProjectStart/صوره/jeem.png) | **Haa (ح)** | ![Haa Skeleton](c:/Users/mohammed/ProjectStart/صوره/haa.png) |
| **Khaa (خ)** | ![Khaa Skeleton](c:/Users/mohammed/ProjectStart/صوره/khaa.png) | **Dal (د)** | ![Dal Skeleton](c:/Users/mohammed/ProjectStart/صوره/dal.png) |
| **Thal (ذ)** | ![Thal Skeleton](c:/Users/mohammed/ProjectStart/صوره/thal.png) | **Ra (ر)** | ![Ra Skeleton](c:/Users/mohammed/ProjectStart/صوره/ra.png) |
| **Zay (ز)** | ![Zay Skeleton](c:/Users/mohammed/ProjectStart/صوره/zay.png) | **Seen (س)** | ![Seen Skeleton](c:/Users/mohammed/ProjectStart/صوره/seen.png) |
| **Sheen (ش)** | ![Sheen Skeleton](c:/Users/mohammed/ProjectStart/صوره/sheen.png) | **Saad (ص)** | ![Saad Skeleton](c:/Users/mohammed/ProjectStart/صوره/saad.png) |
| **Daad (ض)** | ![Daad Skeleton](c:/Users/mohammed/ProjectStart/صوره/daad.png) | **Taa (ط)** | ![Taa Skeleton](c:/Users/mohammed/ProjectStart/صوره/taa.png) |
| **Zaa (ظ)** | ![Zaa Skeleton](c:/Users/mohammed/ProjectStart/صوره/zaa.png) | **Ain (ع)** | ![Ain Skeleton](c:/Users/mohammed/ProjectStart/صوره/ain.png) |
| **Ghain (غ)** | ![Ghain Skeleton](c:/Users/mohammed/ProjectStart/صوره/ghain.png) | **Fa (ف)** | ![Fa Skeleton](c:/Users/mohammed/ProjectStart/صوره/fa.png) |
| **Qaaf (ق)** | ![Qaaf Skeleton](c:/Users/mohammed/ProjectStart/صوره/qaaf.png) | **Kaaf (ك)** | ![Kaaf Skeleton](c:/Users/mohammed/ProjectStart/صوره/kaaf.png) |
| **Laam (ل)** | ![Laam Skeleton](c:/Users/mohammed/ProjectStart/صوره/laam.png) | **Meem (م)** | ![Meem Skeleton](c:/Users/mohammed/ProjectStart/صوره/meem.png) |
| **Noon (ن)** | ![Noon Skeleton](c:/Users/mohammed/ProjectStart/صوره/noon.png) | **Haa (هـ)** | ![Haa2 Skeleton](c:/Users/mohammed/ProjectStart/صوره/haa_final.png) |
| **Waw (و)** | ![Waw Skeleton](c:/Users/mohammed/ProjectStart/صوره/waw.png) | **Ya (ي)** | ![Ya Skeleton](c:/Users/mohammed/ProjectStart/صوره/ya.png) |

*[Note: These images represent the 2D keypoint projections used to calculate the distances for classification during the training phase.]*

### 3.9 Model Performance and Evaluation
To ensure high classification precision, the keypoint classifier was trained on a custom dataset of thousands of landmarks. The training process followed a 80-20 split (Training vs. Testing). 

#### 3.9.1 Training Metrics Analysis
The model’s overall performance was monitored via accuracy and loss metrics, achieving a peak validation accuracy of **98.2%**. Several key insights arise from these results:

1.  **Fast Convergence (Figure 3.9):** The model reached its high accuracy within just **200 epochs**, with the **Loss Curve** showing a smooth exponential decay. This confirms that the network was efficiently learning the complex geometric patterns of the 21 finger landmarks.
2.  **Generalization:** The close alignment between the training and validation curves in (Figure 3.9) indicates that the model is **Generalizing** well. This proves that the system can recognize hand shapes and gestures from different users with various hand sizes, ensuring the application remains robust across the entire ArSL alphabet.

![Figure 3.9: Training Accuracy and Loss Curves for the Keypoint Classifier](c:/Users/mohammed/ProjectStart/صوره/learning_curves.png)

#### 3.9.2 Confusion Matrix Analysis
A detailed analysis of the **Confusion Matrix (Figure 3.10)** shows that the system is highly accurate for distinct signs like 'Alif' (أ) and 'Ba' (ب). Minor misclassifications were observed between letters with high geometric similarity, such as 'Ta' (ت) and 'Tha' (ث), depending on the camera angle. However, these errors were statistically insignificant for overall system usability.

The concentration of high values along the primary diagonal demonstrates the model's exceptional precision across the entire 28-letter sign alphabet. Furthermore, the low density of off-diagonal values confirms that the integrated MediaPipe hand-landmark system provides sufficient resolution to capture subtle variations in finger joint angles, even in cases of partial occlusion. This high degree of separation between classes ensures that the system provides reliable real-time communication without confusing the end-user with incorrect character translations.

![Figure 3.10: Confusion Matrix for the 28 Arabic Sign Language Letters](c:/Users/mohammed/ProjectStart/صوره/output.png)


# **Chapter Four: Results and Discussion**

### 4.1 Introduction
With the system implementation and model training detailed in Chapter Three, this chapter focuses on the real-world experimental results. We evaluate the holistic performance of the integrated pipeline on the Raspberry Pi 4 platform, specifically focusing on latency, environmental robustness, and a comparative analysis against existing ArSL literature.

### 4.2 Real-time Performance and System Speed
A critical metric for any assistive technology is the "Latency" or the responsiveness of the system when converting a physical gesture into a digital output.

*   **Frame-Per-Second (FPS):** On the Raspberry Pi 4 Model B, the system maintained a stable output of **24-30 FPS**. This high-speed performance was achieved by utilizing the TFLite inference engine and the MediaPipe Tasks API, which are optimized for ARM-based processors.
*   **Stability Performance:** The custom "Temporal Stability Logic" described in section 3.4.2 was validated during testing. Before its implementation, character flicker was frequent; after activation, the output stability improved by over **85%**, resulting in a smooth, professional user experience.

### 4.3 Environmental Robustness Testing
To ensure the system is viable for daily use outside laboratory conditions, it was tested across varying environments:
1.  **Variable Lighting Conditions:** The system functioned reliably in bright daylight and standard indoor lighting. A significant drop in accuracy was only observed in near-dark conditions where landmarks could not be reliably extracted.
2.  **User Positioning:** Maximum detection accuracy was maintained at distances between **0.5m and 1.5m** from the Rapoo C200 lens. Accuracy began to degrade beyond 2 meters as the hand landmarks became too small for precise calculation.

![Figure 4.3: Robustness Analysis - Accuracy across Different Lighting and Distances](c:/Users/mohammed/ProjectStart/صوره/robustness_analysis.png)

### 4.4 Comparison and Discussion
The proposed system was compared against previous ArSL research paradigms based on several technical benchmarks. The following table illustrates the strategic advantages of our approach:

![Table 4.1: Comparison Between Previous Studies and Proposed ArSL System](c:/Users/mohammed/ProjectStart/صوره/comparison_table.png)

In summary, the transition to **Landmark-based Edge AI** allows this project to outperform many desktop-bound systems by providing a portable, low-latency, and high-accuracy (98.2%) translation bridge for the deaf community.

### 4.5 Summary of Findings and System Stability
The comprehensive testing phase confirms that the proposed ArSL recognition system is not only a technical success but also a viable practical tool. The key findings are summarized as follows:
*   **Operational Stability:** The integration of the "Temporal Stability Buffer" ensures that the system provides intentional, stutter-free translations even under slight hand tremors.
*   **Usability:** The "Glassmorphism" web interface provides a modern, eye-friendly layout that supports real-time Arabic text reshaping and natural audio feedback.
*   **Hardware Efficiency:** The Raspberry Pi 4 maintained consistent performance without thermal throttling or overheating, proving highly reliable throughout the evaluation period.

---


# **Chapter Five: Conclusion and Future Research**

### 5.1 Conclusion
This research successfully demonstrates the potential of Edge AI for assistive technology, specifically in translating the 28-letter Arabic Sign Language (ArSL) alphabet on a portable platform. By combining the **Raspberry Pi 4** with the **MediaPipe Tasks API**, we achieved a stable and highly accurate real-time inference rate of **24-30 FPS**, providing a seamless experience for deaf and hard-of-hearing users.

The core success of this system lies in the transition from computationally expensive image-based processing to **landmark-based keypoint classification**. This optimization allowed high-precision recognition (98.2% accuracy) on low-power hardware, proving that reliable accessibility tools can be built without the need for expensive GPU-driven workstations. Furthermore, the integration of **Temporal Stability Buffering** and **Microsoft Edge-TTS** transformed a raw classifier into a complete communication bridge, offering both visual and auditory feedback in a modern "Glassmorphism" web interface. 

### 5.2 Future Research
While the project achieved its primary objectives, several avenues for future work have been identified to increase its impact:
1.  **Sentence-Level Recognition:** Transitioning from individual letter classification to continuous sign language recognition using **Long Short-Term Memory (LSTM)** or **Transformer** networks to interpret sequences of gestures into sentences.
2.  **Two-Handed Signing Support:** Enhancing the dataset and model architecture to detect and classify complex signs involving two-handed interactions and spatial relationships.
3.  **Facial Expression Integration:** Incorporating facial landmark detection to capture non-verbal cues, which are vital for conveying the full emotional and linguistic nuances of sign language.
4.  **Cross-Platform Portability:** Developing dedicated mobile applications (Android/iOS) to leverage the same lightweight TFLite architecture, making the tool even more accessible for users on the go.

In conclusion, this project provides a scalable, low-cost framework that breaks down communication barriers for the deaf community in the Arab world, fulfilling both technical efficiency and social responsibility.

