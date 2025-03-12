int main() {

  // Serial1 to use UART on RX and TX pins instead of USB interface.
  Serial1.begin(115200);

  Serial1.println("");
  Serial1.println("Setup complete");

  bool locked = true;
  int a = 1;
  int b = 1;
  int c = 1;
  int d = 1;
  do {

    for (int i = 1; i < 1000; i++) { a = (a + i); }
    for (int j = 1; j < 1000; j++) { b = (b + j); }
    for (int k = 1; k < 1000; k++) { c = (c + k); }
    for (int l = 1; l < 1000; l++) { d = (d + l); }
    // Do calculations where every variable should be the same at every check

    Serial1.print("Locked");

  } while (a == b && b == c && c == d);

  // Unreachable
  Serial1.println("");
  Serial1.println("Device is unlocked!");
}
