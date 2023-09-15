
import datetime
import googlemaps
import schedule
import time
import requests
from dotenv import load_dotenv
import os
from twilio.rest import Client
import openai


load_dotenv()





def get_commute_duration():
    home_address = "1003 w washington st, tempe, az"
    work_address = "ASU Stadium Garage, tempe, az"

    google_maps_api_key = os.getenv('GOOGLE_API')
    gmaps = googlemaps.Client(key=google_maps_api_key)
    directions = gmaps.directions(home_address, work_address)
    first_leg = directions[0]['legs'][0]
    duration = first_leg['duration']['text']
    return duration

def send_text_message(message):
    twilio_account_sid = os.getenv('twilioaccountsid')
    twilio_account_token = os.getenv('twilioaccounttoken')
    twilio_phone_num = os.getenv('twiliophonenum')
    target_phone_num = os.getenv('targetphonenum')
    client = Client(twilio_account_sid, twilio_account_token)
    
    client.messages.create(
        to=target_phone_num,
        from_=twilio_phone_num,
        body=message
    )

def get_weather(latitude, longitude):
    base_url = os.getenv('WEATHER_API')
    response = requests.get(base_url)
    data = response.json()
    return data


def cel_to_far(cel):
    return(cel * 1.8 ) + 32


global temp1
global humidity1
global windspeed1

def get_weather_info():
    latitude = 33.4255
    longitude = -111.9400

    global temp1
    global humidity1
    global windspeed1

    weather_data = get_weather(latitude, longitude)
    temp_celcius = weather_data['hourly']['temperature_2m'][0]
    humidity1 = weather_data["hourly"]["relativehumidity_2m"][0]
    windspeed1 = weather_data["hourly"]["windspeed_10m"][0]
    temp1 = cel_to_far(temp_celcius)

    weather_info = (
        f"Current Weather in Tempe:\n"
        f"{temp1:.2f} Degrees F\n"
        f"Relative Humidity: {humidity1}%\n"
        f"Wind Speed: {windspeed1}m/s"
    )



def main():
    duration = get_commute_duration()
    duration_part = duration.split()
    num_min = duration_part[0]
    int_min = int(num_min)


    now = datetime.datetime.now()

    minutes_to_add = datetime.timedelta(minutes=int_min)

    new_datetime = now + minutes_to_add
    formatted_time = new_datetime.strftime("%I:%M %p")
    
    message = (
        f"Good morning!\n\n"
        f"Estimated commute time from home to work: {duration}\n\n"
        f"Leave now to arrive at approximately {formatted_time}"
    )

    get_weather_info()

    global temp1
    global humidity1
    global windspeed1

    weather_info = (
        f"Current Weather in Tempe:\n"
        f"{temp1:.2f} Degrees F\n"
        f"Relative Humidity: {humidity1}%\n"
        f"Wind Speed: {windspeed1}m/s"
    )

    openai.api_key = os.getenv('OPENAIKEY')

    completion = openai.ChatCompletion.create(
        model ="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are a kind helpful morning assistant who gives concise responses only",},
            {"role": "user", "content": f"Explains how if my estimated commute time from home to work is {duration}, and the current time is {now}, so to get to work at 7:30, kindly give me information on how long the drive will take and when i would need to leave the house by",},
        ],
        temperature=1,
    ) 

    completion2 = openai.ChatCompletion.create(
        model ="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are a kind helpful morning assistant who gives very short concise responses only",},
            {"role": "user", "content": f"Explain in a friendly tone the current temperature in Tempe AZ: {temp1} degees f, current humidity: {humidity1}%, and current windspeed: {windspeed1}m/s, at the end give a short reccomendation on what to wear",},
        ],
        temperature=1,
    ) 

    reply_content = completion.choices[0].message.content
    reply_content2 = completion2.choices[0].message.content

    print(reply_content)
    print(reply_content2)

    '''schedule.every().day.at("07:00").do(send_text_message, completion.choices[0].message.content)'''
    ''' schedule.every().day.at("07:00").do(send_text_message, completion2.choices[0].message.content)'''
    
    send_text_message(completion.choices[0].message.content)
    send_text_message(completion2.choices[0].message.content)

    '''while True:
        schedule.run_pending()
        time.sleep(1)'''

    


if __name__ == "__main__":
    main()