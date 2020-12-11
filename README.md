[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]


<!-- PROJECT LOGO -->
<br />
<p align="center">
  <h3 align="center">PDF Scraper and Language Detector</h3>

  <p align="center">
    A technical overview of the Scraping PDF Tabular data and Detect Language of the PDF Docuemnt.
  </p>
    <br />
    <a href="https://github.com/virajds/PDFTools"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/virajds/PDFTools">View Demo</a>
    ·
    <a href="https://github.com/virajds/PDFTools/issues">Report Bug</a>
    ·
    <a href="https://github.com/virajds/PDFTools/issues">Request Feature</a>
  </p>
</p>

<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)


<!-- ABOUT THE PROJECT -->
## About The Project

This project manages two tasks.

1. PDF Tabular Data to JSON export
2. Detect language of both Image based and Text based PDFs

### Built With
This is an open source project; built with;

* [Pyhton](https://www.python.org/)
* [pytesseract](https://pypi.org/project/pytesseract/)
* [Pillow](https://pypi.org/project/Pillow/)
* [pdfminer](https://pypi.org/project/pdfminer/)
* [langid](https://pypi.org/project/langid/)

<!-- GETTING STARTED -->
## Getting Started

Project can be started by Cloning the GitHub and Installing required Packages.

### Prerequisites

* python3.8
```
$ sudo apt update -y
$ sudo apt install python3.8
```

* create a virtual environment

```
cd <Project DIR>
python3 -m venv venv
```

* Activate virtual environment
```
source venv/bin/activate
```

### Installation

* Clone the repo
```sh
git clone https://github.com/virajds/PDFTools
```

* Install packages

```sh
pip install -r PDFTools/requirements.txt
```

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/virajds/PDFTools.svg?style=flat-square
[contributors-url]: https://github.com/virajds/PDFTools/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/virajds/PDFTools.svg?style=flat-square
[forks-url]: https://github.com/virajds/PDFTools/network/members
[stars-shield]: https://img.shields.io/github/stars/virajds/PDFToolssvg?style=flat-square
[stars-url]: https://github.com/virajds/PDFTools/stargazers
[issues-shield]: https://img.shields.io/github/issues/virajds/PDFTools?style=flat-square
[issues-url]: https://github.com/virajds/PDFTools/issues
[license-shield]: https://img.shields.io/github/license/virajds/PDFTools.svg?style=flat-square
[license-url]: https://github.com/virajds/PDFTools/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/viraj-de-silva-85644b10/
[product-screenshot]: ../images/screenshot.png