import aiohttp
from geopy.geocoders import Nominatim as Geolocator
from config import OpenMapsAPIKey
from humanfriendly.tables import format_pretty_table as boop
import discord

async def weather(cmd, message, args):
    
    if not args:
        await message.channel.send(cmd.help())
        return

    if OpenMapsAPIKey == '':
        embed = discord.Embed(color=0xDB0000)
        embed.add_field(name='API key OpenMapsAPIKey not found.', value='Please ask the bot owner to add it.')
        await message.channel.send(None, embed=embed)
        return

    location = ' '.join(args)
    
   ##try:
    if True:
        try:
            loc_element = Geolocator().geocode(location)
            latitude = loc_element.latitude
            longitude = loc_element.longitude
        except Exception as e:
            cmd.log.error(e)
            await message.channel.send('Unable to retrieve coordinates for ' + location)
            return

        openWeatherURL = 'http://api.openweathermap.org/data/2.5/weather?lat=' + str(latitude) + '&lon=' + str(longitude) + "&cnt=1&units=imperial&APPID=" + OpenMapsAPIKey
        async with aiohttp.ClientSession() as session:
            async with session.get(openWeatherURL) as data:
                data = await data.json()

        temp_f = data['main']['temp']
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        wind_speed_mph = data['wind']['speed']
        wind_bearing = data['wind']['deg']
        cloud_cover = data['clouds']['all']
        
        wind_speed_kph = wind_speed_mph * 1.609344
        temp_c = (temp_f - 32) / 1.8    
        
        # Data Output
        out_list = []

        out_list.append(['Temperature', str(format(temp_c, '.2f')) + '°C (' + str(temp_f) + '°F)'])
        out_list.append(['Humidity', str(humidity) + '%'])
        out_list.append(['Wind Speed', str(format(wind_speed_kph, '.2f')) + ' KPH (' + str(wind_speed_mph) + ' MPH)'])
        out_list.append(['Wind Direction', str(wind_bearing) + '°'])
        out_list.append(['Cloud Cover', str(cloud_cover) + '%'])
        out_list.append(['Pressure', str(pressure) + ' mb'])

        out_pretty_list = boop(out_list)

        out_text = 'Weather data for **' + location.title() + '**\nLocation: *(Lat: ' + str(latitude) + ', Long: ' + str(longitude) + ')*'
        out_text += '\n```haskell\n' + out_pretty_list + '\n```'
#        forecasts = '```haskell\nUpcoming: \"' + today_forecast + '\"\nThis Week: \"' + week_forecast + '\"\n```\n'
#       out_text += '\nForecasts:\n' + forecasts
        await message.channel.send(out_text)
    
  #  except Exception as e:
   #     cmd.log.error(e)
    #    await message.channel.send('Error Retrieving the data.')
