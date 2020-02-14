# Autonomous Delivery System

This is a repository for Autonomous Delivery System project by Nozama-Hotmetal. This was a project organized by [IITP](https://ezone.iitp.kr/common/anno/02/form.tab?PMS_TSK_PBNC_ID=PBD201900000075)-[CMU](https://www.cmu.edu/). Related article about the program can be found [here](http://www.donga.com/news/article/all/20190819/97023944/1). The final documentation including Project Description, Architectural Drivers, Architectural Designs can be found in `documentation.pdf`.



## Dependencies

All the python dependencies used in the project are listed the `requirements.txt`.

```
pip install -r requirements.py
```



## Project Structure

Project consists of 5 main modules: `main_server`, `order_server`, `robot`, `scheduler`. Each module communicates with SocketIO, so it can run on different machine. `robot` must run on Raspberri-pi machine.

```bash
├── main_server       # Main server connecting robot, scheduler, and UI
├── order_server      # Web server for accepting orders
├── robot							# Runs on Raspberri-pi
├── scheduler
├── order_simulator
├── document.pdf
└── requirements.txt
```



## Architectural Design

This is diagram showing dynamic view of the system. A detailed explanation and different view can be found in the `documentation.pdf`.

![dynamic_view](https://i.imgur.com/gAU1rPF.png)

