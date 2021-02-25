# Smart Mirror RORRIM

*THIS IS AN ARCHIEVED VERSION OF THE PROJECT, LAST UPDATED IN DECEMEBER 2020*

Smart Mirror RORRIM is a health-centric smart mirror that incorporates non-invasive devices to help end-users monitor health information such as: sleep cycle, step count, BPM, etc.

Please refer to **RORRIM Poster.pdf** and **RORRIM Report.pdf** for more information


Please watch [our demo video](https://youtu.be/KO6M1vGY9kg) for our submission for Fall Design Review 2020


Our current implementation has the following:
* Displays a home screen with standard smart mirror widgets, such as time and weather
* Displays simple health information from Fitbit: heart rate and step count
* Uses facial identification to recognize different users and store information
* Accepts Touch Input
* Sync health information from Fitbit for machine learning to create health recommendations
* Integrate PIR sensor to detect motion 


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the following:

```bash
pip install python3-opencv
pip install cmake
pip install https://pypi.python.org/packages/da/06/bd3e241c4eb0a662914b3b4875fc52dd176a9db0d4a2c915ac2ad8800e9e/dlib-19.7.0-cp36-cp36m-win_amd64.whl#md5=b7330a5b2d46420343fbed5df69e6a3
pip install face_recognition
pip install scikit-image
```

## Usage

The materials we used are as follows:
* Raspberry Pi 3 B+
* Raspberry Pi NOIR Camera Module V2
* HC-SR501 PIR Motion Sensor
* Sceptre E248W-19203R 24'' LCD Monitor
* Reflective Film
* Acrylic Sheet
* Fitbit Sense

RORRIM's central computer is a Raspberry Pi. A Raspberry Pi Camera is used for facial recognition. A passive infrared (PIR) sensor is used for motion detection. When connecting the PIR Sensor, connect the input pin to pin 22, as mentioned in **/face/SensorLED.py**

To run, type the following command in your terminal:
```bash
python home_screen.py
```

## Contributors
RORRIM consists of the following members:
* Carissa Sevaston
* Johnathan Tang
* Bryan Trinh
* Isabelle Wang
* Kevin Zhu
