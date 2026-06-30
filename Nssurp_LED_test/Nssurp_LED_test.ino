/// @file    NSpikeShoe.ino
/// @brief   Get data from an accelerometer and make a chain of LEDs on the shoe respond


#include <FastLED.h>
#include <stdio.h>

#define DATA_PIN 2


// How many leds in your strip?
#define NUM_LEDS 82



//Global timers for keeping track of loop things
unsigned long g_timer_0 = 0;

float duration, distance;
int wait = 1;
int color_base = 0;
int color;
int sat;
int bright;
char state[30];
int a, b, c, d;
bool blinking = false;
bool increase = true; // Starts by going up to the larger color value
int curCol = -1;
bool fadeIn = false;
int fadeBright = 255;


// Cycle for LED blinking
#define CYCLE_TIME 100


// Define the array of leds
CRGB leds[NUM_LEDS];


void setup() { 
 
  Serial.begin(115200);

  // Set up LEDs
  FastLED.addLeds<WS2811, DATA_PIN, RGB>(leds, NUM_LEDS);
  sat = 255;
  bright = 255;

  // Set LEDs to white on start
  for(int i = 0; i < NUM_LEDS; i = i + 1)
        leds[i] = CHSV(0, 0, 0);
  FastLED.show();
  delay(wait);
}



void loop() { 

  // Write LEDs
  color_base = 0;

  // Colors use the "Spectrum" color map
  //instant(171,1); // Needs a color int and a wait time
  //dim(100, 1); // Needs a value to dim by and a wait time
  //rainbow(1); // Only needs a wait time
  //facing(9, 1, 160, 0, 1); // Needs a place to change color at, distance to change color around, default color, secondary color, and a wait time
  //spin(10, 171, 0, 50); // Needs a range to spin, color that is spun, a background color, and a speed
  //pulse(85, 2, 1, 255, 100); // Needs a color to pulse, rate to change, time to wait, max brightness, and min brightness
  //fade(85, 5, 10); // Needs a color to fade, a rate to fade at, and a time to wait
  //fadeTo(0, 255, 5, 10); // Needs two colors to fade between, a rate to fade at, and a time to wait
  //turn(42, false, 500); // Needs a turn color, a direction boolean, a blink time, and a wait time
  //alternate(171,255,1); // Needs a color for even leds, a color for odd leds, and a wait time

    if(Serial.available() > 0)
    {
      String piData = Serial.readStringUntil('\n');

      if (piData != NULL)
        sscanf(piData.c_str(), "%s %d %d %d", state, &a, &b, &c, &d);
    }
    
    const char *inst_state = "instant";
    const char *dim_state = "dim";
    const char *rainbow_state = "rainbow";
    const char *facing_state = "facing";
    const char *spin_state = "spin";
    const char *pulse_state = "pulse";
    const char *fade_state = "fade";
    const char *fadeTo_state = "fadeTo";
    const char *turn_state = "turn";
    const char *alt_state = "alternate";
    
    if (strcmp(state,inst_state) == 0)
      instant(a,b);
    else if (strcmp(state,dim_state) == 0)
      dim(a,b);
    else if (strcmp(state,rainbow_state) == 0)
      rainbow(a);
    else if (strcmp(state,facing_state) == 0)
      facing(a,16,b,c,d);
    else if (strcmp(state,spin_state) == 0)
      spin(a,b,c,d);
    else if (strcmp(state,pulse_state) == 0)
      pulse(b, a, c, 255, 100);
    else if (strcmp(state,fade_state) == 0)
      fade(b,a,c);
    else if (strcmp(state,fadeTo_state) == 0)
      fadeTo(b,c,a,d);
    else if (strcmp(state,turn_state) == 0)
    {
      if (a == 1)
        turn(42, true, b);
      else
        turn(42, false, b);
    }
    else if (strcmp(state,alt_state) == 0)
      alternate(a,b,c);
    else
      off(1);
    FastLED.show();
    delay(wait);
}

//No lights on
void off(int waitTime)
{
  for(int i = 0; i < NUM_LEDS; i++)
  {
    leds[i] = CHSV(0, 0, 0);
    delay(waitTime);
  }
  FastLED.show();
}

// Instant color change
void instant(int instantColor, int waitTime)
{
  color = instantColor;
  
  for(int i = 0; i < NUM_LEDS; i++)
  {
    leds[i] = CHSV(color, sat, bright);
    delay(waitTime);
  }
  FastLED.show();
}

void dim(int dim, int waitTime)
{
  for(int i = 0; i < NUM_LEDS; i++)
  {
    leds[i].fadeLightBy(dim);
    delay(waitTime);
  }
  FastLED.show();
}

// Rainbow of color around the strip, conforms to strip length
void rainbow(int waitTime) {
  for(int i = 0; i < NUM_LEDS; i = i + 1) {
   color = round(((float)i)/NUM_LEDS * 255);
   leds[i] = CHSV(color, sat, bright);
   FastLED.show();
   delay(waitTime);
  }
}

// Changes color around 'place' in the LED array
void facing(int place, int distance, int defaultColor, int faceColor, int waitTime) {
  for(int i = 0; i < NUM_LEDS; i++)
  {
    if (abs(i-place) <= distance)
      leds[i] = CHSV(faceColor, sat, bright);
    else if (i-place < 0)
    {
      if (abs(i+NUM_LEDS-place) <= distance)
        leds[i] = CHSV(faceColor, sat, bright);
      else
        leds[i] = CHSV(defaultColor, sat, bright);
    }
    else if (place-i < 0)
    {
      if (abs(place-i+NUM_LEDS) <= distance)
        leds[i] = CHSV(faceColor, sat, bright);
      else
        leds[i] = CHSV(defaultColor, sat, bright);
    }
    else
      leds[i] = CHSV(defaultColor, sat, bright);

    //FastLED.show();
    delay(waitTime);
  }
  FastLED.show();
}

// Spins an area of 'range' leds of 'spinColor' along the background of'baseColor'
void spin(int range, int spinColor, int baseColor, int waitTime)
{
  for(int i = 0; i < NUM_LEDS; i++)
  {
    int place = i-range;
    if (place < 0)
      place = NUM_LEDS-(range-i);
    
    leds[i] = CHSV(spinColor, sat, bright);
    leds[place] = CHSV(baseColor, sat, bright);
    FastLED.show();
    delay(waitTime);
  }
}

// Pulses 'col' constantly between 'maxBri' and 'minBri'
void pulse(int col, int pulseSpeed, int waitTime, int maxBri, int minBri)
{
  color = col;
  bright -= pulseSpeed;
  if (bright < minBri)
    bright = maxBri;
  for(int i = 0; i < NUM_LEDS; i++)
    leds[i] = CHSV(color, sat, bright);
  FastLED.show();
  delay(waitTime);
}

// Fades in and out constantly at 'fadeRate' speed
void fade(int col, int fadeRate, int waitTime)
{
  color = col;
  if (fadeIn)
  {
    fadeBright += fadeRate;
    if (fadeBright + fadeRate > 255)
      fadeIn = false;
  }
  else
  {
    fadeBright -= fadeRate;
    if (fadeBright - fadeRate < 0)
      fadeIn = true;
  }
  for (int i = 0; i < NUM_LEDS; i++)
    leds[i] = CHSV(color, sat, fadeBright);
  FastLED.show();
  delay(waitTime);
}

// Fades from 'color1' to 'color2'  at 'fadeRate' time (seconds)
void fadeTo(int color1, int color2, int fadeRate, int waitTime)
{
  if (curCol == -1)
    curCol = min(color1, color2); // Starts at the smaller color value

  if (increase)
  {
    curCol += fadeRate;
    if (curCol >= max(color1, color2))
      increase = false; // Needs to start going down
  }
  else
  {
    curCol -= fadeRate;
    if (curCol <= min(color1, color2))
      increase = true; // Needs to start going up
  }
  
  for (int i = 0; i < NUM_LEDS; i++)
    leds[i] = CHSV(curCol, sat, bright);
  FastLED.show();
  delay(waitTime);
}

// Looks like a turn signal. Boolean 'turn': left is true, right is false
// Turn signal color is the left/right (area) of the LED strip, assuming back right is 0 and back left is NUM_LEDS
void turn(int turnColor, bool turn, int waitTime)
{
  for (int i = 0; i < NUM_LEDS; i++)
  {
    if (blinking)
      leds[i] = CHSV(turnColor, sat, 0);
    else
    {
      if (turn) // Left
      {
        if (i > NUM_LEDS * 5/8 && i < NUM_LEDS * 7/8)
          leds[i] = CHSV(turnColor, sat, bright);
        else
          leds[i] = CHSV(turnColor, sat, 0);
      }
      else // Right
      {
        if (i > NUM_LEDS * 1/8 && i < NUM_LEDS * 3/8)
          leds[i] = CHSV(turnColor, sat, bright);
        else
          leds[i] = CHSV(turnColor, sat, 0);
      }
    }
  }
  
  if (blinking)
    blinking = false;
  else
    blinking = true;
  
  FastLED.show();
  delay(waitTime);
}

void alternate(int color1, int color2, int waitTime)
{
  for(int i = 0; i < NUM_LEDS; i++)
  {
    if (i % 2 == 0) //Even
      leds[i] = CHSV(color1, sat, bright);
    else //Odd
      leds[i] = CHSV(color2, sat, bright);
      
    FastLED.show();
    delay(waitTime);
  }
}
