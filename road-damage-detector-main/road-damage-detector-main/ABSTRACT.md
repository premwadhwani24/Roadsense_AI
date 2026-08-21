**RDD2022: The Multi-National Road Damage Dataset 2022** comprises 47,420 road images from six countries, Japan, India, the Czech Republic, Norway, the United States, and China. The images have been annotated with more than 55,000 instances of road damage. Five types of road damage, namely *longitudinal crack*, *transverse crack*, *alligator crack*, *pothole* and *other corruption* are captured in the dataset. The annotated dataset is envisioned for developing deep learning-based methods to detect and classify road damage automatically. The dataset has been released as a part of the Crowd sensing-based Road Damage Detection Challenge [(CRDDC’2022)](https://crddc2022.sekilab.global/). The challenge CRDDC’2022 invites researchers from across the globe to propose solutions for automatic road damage detection in multiple countries.

<img src="https://github.com/dataset-ninja/road-damage-detector/assets/120389559/9541583b-9965-4e25-b2ae-715b3331dc96" alt="image" width="1000">

<span style="font-size: smaller; font-style: italic;">Sample images for road damage categories considered in the data. a. Longitudinal Crack (D00), b. Transverse Crack (D10), c. Alligator Crack (D20), d. Pothole (D40).</span>

## Dataset Description

* **Japan:** The data is collected from seven local governments in Japan (Ichihara city, Chiba city, Sumida ward, Nagakute city, Adachi city, Muroran city, and Numazu city). The municipalities have snowy and urban areas that vary widely from the perspective of regional characteristics like weather and budgetary constraints.

* **India:** The data from India includes images captured from local roads, state highways, and national highways, covering the metropolitan (Delhi, Gurugram) as well as non-metropolitan regions (mainly from the state of Haryana). All these images have been collected from plain areas. Road selection and time of data collection were decided based on road accessibility, atmospheric conditions, and traffic volume.

* **Czech Republic:** A substantial portion of road images was collected in Olomouc, Prague, and Bratislava municipalities and covered a mix of first-class, second-class, and third-class roads and local roads. A smaller portion of the road image dataset was collected along D1, D2, and D46 motorways to enhance the resilience of the targeted model. 

* **Norway:** The data from Norway consists of two classes of roads Expressways and County Roads (or Low Volume Roads). Both types of road classes are asphalt pavements. Data collection is done by the Norwegian Public Road Administration (Statens Vegvesen, SVV) and Inlandet Fylkeskommune (IFK). Images provided by SVV were collected on European Route E14, connecting the city of Trondheim in Norway to Sundsvall in Sweden. At the same time, the images from IFK belong to different county roads within Inllanndet County in Norway. The images were collected without any control over daytime/light, and all the images are natural without further processing. Further, the dataset captures diverse backgrounds, including clear grass fields, snow-covered areas, and conditions after rain. Furthermore, images with different illuminances, such as high sunlight and overcast weather resulting in daylight, are considered. 

* **United States:** The data from the United States consists of Google Street View images covering multiple locations, including California, Massachusetts, and New York.

* **China:** RDD2022 considers two types of data from China: (a) images captured by drone(***China_Drone***), and (b) the images captured using Smartphone-mounted motorbike(***China_MotorBike***). The ***China_Drone*** images were obtained from Dongji Avenue in Nanjing, China. The ***China_MotorBike*** images were collected on Jiu long hu campus, Southeast University. Images with normal light, under a shadow environment, and wet stains are covered.

Asphalt concrete pavement is considered with a few exceptions in all six subsets of RDD2022. Each road damage in dataset has ***detail*** definitions.

<img src="https://github.com/dataset-ninja/road-damage-detector/assets/120389559/1511af40-a0f2-413f-93b7-c5dffe602eda" alt="image" width="800">

<span style="font-size: smaller; font-style: italic;">Damage Category-based data statistics for RDD2022.</span>

## Image Acquisition

The images in RDD2022 have been acquired using different methods for different countries. For India, Japan, and the Czech Republic, smartphone-mounted vehicles (cars) were utilized to capture road images. In some cases, the setup with the smartphone mounted on the windshield (inside the car) was also used. Images of resolution 600x600 are captured for Japan and the Czech Republic. For India, images are captured at a resolution of 960x720 and later resized to 720x720 to maintain uniformity with the data from Japan and the Czech Republic.

<img src="https://github.com/dataset-ninja/road-damage-detector/assets/120389559/eaa26e94-955e-480e-8d14-aedce3599704" alt="image" width="800">

<span style="font-size: smaller; font-style: italic;">Sample Installation Setup of the smartphone in the car: Image acquisition for data from India, Japan, and the Czech Republic.</span>

For Norway, instead of smartphones, high-resolution cameras mounted inside the windshield of a specialized vehicle, ViaPPS, were used for data collection.

<img src="https://github.com/dataset-ninja/road-damage-detector/assets/120389559/fabcf7fd-5c41-4867-bef6-5da884f10a42" alt="image" width="800">

<span style="font-size: smaller; font-style: italic;">ViaPPS vehicle used to collect data from Norway.</span>

ViaPPS System employs two Basler_Ace2040gc cameras with Complementary metal oxide semiconductor (CMOS) sensor to capture images and then stitches them into one wide view image of a typical resolution 3650x2044.

<img src="https://github.com/dataset-ninja/road-damage-detector/assets/120389559/91e4837c-ab26-4b76-b776-a8f7a25301a5" alt="image" width="800">

<span style="font-size: smaller; font-style: italic;">Camera set-up in the ViaPPS vehicle used to collect data from Norway.</span>

In contrast, the data for the United States comprises Google Street View Images (vehiclebased) of the resolution 640x640. Likewise, for China, two types of image-acquisition methods are considered. The first method includes a camera mounted on motorbikes moving at an average speed of 30km/h; the corresponding dataset is referred to as China_MotorBike or China_M. The second method uses a six-motor UAV manufactured by DJI (M600 Pro) for pavement image collection, resulting in China_Drone (or China_D) data. A controllable three-axis gimbal was mounted at the bottom of the UAV to hold the camera and allow 360-degree rotation for capturing the China_Drone data. The resolution of images for the data from China is 512x512.

<img src="https://github.com/dataset-ninja/road-damage-detector/assets/120389559/554a4e10-4cee-4c1f-a283-f1c434de710d" alt="image" width="800">

<span style="font-size: smaller; font-style: italic;">The drone and camera set-up used to capture China_Drone data included in RDD2022.</span>

## Dataset Annotation

RDD2022 includes annotation for road damage present in the image. The software [LabelImg](https://github.com/heartexlabs/labelImg) has been used to annotate the images except for the data from Norway. For Norway, another software [Computer Vision Annotation Tool (CVAT)](https://github.com/opencv/cvat), was utilized. All recognized damage instances were annotated by enclosing them with bounding boxes and classified by attaching the proper class label. Class labels and bounding box coordinates, defined by four decimal numbers (xmin, ymin, xmax, ymax), were stored in the XML format.

<img src="https://github.com/dataset-ninja/road-damage-detector/assets/120389559/ba173aaf-2569-45b5-92e5-f1cb482fe75a" alt="image" width="800">

<span style="font-size: smaller; font-style: italic;">Annotation Pipeline (a) input image, (b) image with bounding boxes, \(c\) final annotated image containing bounding boxes and class label (D00 in this case)</span>


