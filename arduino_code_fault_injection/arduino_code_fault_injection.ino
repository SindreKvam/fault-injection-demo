#define LOCK_STATE_PIN 12
#define BUILT_IN_LED_PIN 13

volatile int a = 1, b = 1, c = 1, d = 1;

void setup() {

  pinMode(LOCK_STATE_PIN, OUTPUT);
  pinMode(BUILT_IN_LED_PIN, OUTPUT);

  // Set locked pin high
  digitalWrite(LOCK_STATE_PIN, HIGH);
  digitalWrite(BUILT_IN_LED_PIN, HIGH);

  while(a == b && b == c && c == d) {

    // Do calculations where every variable should be the same at every check
    for(int i = 1; i < 1000; i++){a = (a + i);}
    for(int j = 1; j < 1000; j++){b = (b + j);}
    for(int k = 1; k < 1000; k++){c = (c + k);}
    for(int l = 1; l < 1000; l++){d = (d + l);}

  }

  digitalWrite(LOCK_STATE_PIN, LOW);

}

void loop(){
  // Indicate that the device is unlocked by alternating the LED.
  digitalWrite(BUILT_IN_LED_PIN, LOW);
  delay(500);
  digitalWrite(BUILT_IN_LED_PIN, HIGH);
  delay(500);
}
