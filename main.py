from djitellopy import tello
from gui import UI


def main():
    print("Starting....")
    drone = tello.Tello()
    TelloUi = UI(drone,"./img/")
    # TelloUi.window.mainloop()

if __name__ == "__main__":
    main()
