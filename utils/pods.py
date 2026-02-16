import random

def generate_pods():
    pods = []
    for i in range(1,6):
        pod = {
            "Pod ID": f"Pod-{i}",
            "Speed (km/h)": random.randint(500, 1000),
            "Battery (%)": random.randint(20,100),
            "Status": random.choice(["Operational","Maintenance","Docked"])
        }
        pods.append(pod)
    return pods
