## CarePackage

[![Watch the Video](https://img.youtube.com/vi/vp_H6iF8AbI/maxresdefault.jpg)](https://www.youtube.com/watch?v=vp_H6iF8AbI)

CarePackage is my senior project for my B.S. in Computer Engineering at Chico State. The premise of the project is to provide Biomedical Engineers a comprehensive platform for constructing signal processing pipelines. The project is written in Python and C, and includes some basic algorithms from the Pan Thompkins EKG signal processing paper. 

The application utilizes a variety of architectural design patterns than enable efficient manipulation of the pipeline and easy extensibility in the future. The factory pattern was used to replicate new processing blocks. A linked list is used to store and reconfigure the pipeline architecture. The observer pattern is used to seperate the process logic from the signal rendering logic and enables dynamic UI updates when the pipeline or signal changes. 

I plan to provide support for different data types like images, and eventually package in some machine learning models that have been for classification tasks, possible a platform for training.
