import threading
import sys
import select

class KeyboardInput:
    """ Keyboard input thread """
    def __init__(self) -> None:
        """ Initialize the keyboard input thread """
        self.thread = None
        self.running = False
        self.result = None

    def start(self) -> None:
        """ Start the keyboard input thread """
        if self.running:
            return
        self.thread = threading.Thread(name="Keyboard Input Thread", target=self.main)
        self.thread.start()

    def main(self) -> None:
        """ Main function of the keyboard input thread """
        self.running = True
        self.result = None
        print(">>> ", end="", flush=True)

        while self.running:
            if select.select([sys.stdin], [], [], 0.1)[0]:
                self.result = sys.stdin.readline().strip()
                break

        self.running = False

    def is_result_ready(self) -> bool:
        """ Check if the result is ready

        Returns:
            bool: True if the result is ready, False otherwise
        """
        return self.result is not None

    def stop(self) -> None:
        """ Stop the keyboard input thread """
        if not self.running:
            return
        self.running = False
        self.result = None
        self.thread.join()

if __name__ == "__main__":
    try:
        keyboard_input = KeyboardInput()
        while True:
            keyboard_input.start()
            while True:
                if keyboard_input.is_result_ready():
                    print(f"Received: {keyboard_input.result}")
                    keyboard_input.stop()
                    break
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        keyboard_input.stop()
