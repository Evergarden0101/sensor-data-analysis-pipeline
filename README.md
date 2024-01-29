# Sensor data analysis pipeline

## Description
The Human-Centered Sensor Data Analysis Pipeline presents a comprehensive study of the development and application of a sensor data analysis system focused on human-centric needs. This research integrates advanced visualization tools and health informatics techniques to address critical challenges in medical sciences with high-frequency sensor data. The core of this study revolves around the design and implementation of a visualization system that aids in the efficient analysis and interpretation of complex sensor data.

## Visuals
![Demo of the application](https://gitlab.ifi.uzh.ch/ivda/sensor-data-analysis-pipeline/-/raw/main/front-end/DEMO.gif)

## Installation
### Frontend
- ``npm install -g @vue/cli``
- ``npm install vue-router@4``

### Backend
- Inside back-enfd folder: ``python -m venv .venv``
- macOS: ``source .venv/bin/activate``
- Windows: ``.venv\Scripts\activate``
- ``pip install Flask``
- Initialize database: ``flask --app src/app init-db``


### Requirements
- Flask
- Vue 3

## Usage
- Vue: ``npm run serve``
- Flask: ``flask --app src/app run``
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.


## Authors and acknowledgment
- Eleonora Pura: eleonora.pura@uzh.ch
- Karim Abou el Naga: karim.abouelnaga@uzh.ch
- Yifan Jiang: yifan.jiang@uzh.ch


Thank you to [makeareadme.com](https://www.makeareadme.com/) for this template.
