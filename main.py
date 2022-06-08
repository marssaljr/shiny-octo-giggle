import discord, requests
import urllib
from bs4 import BeautifulSoup
import re
from decouple import config

class MyClient(discord.Client):
	premium = ['mjs#9271']
	users   = []
	friends = ['mjs#9271']

	async def on_ready(self):
		print("Logged on as {0}!".format(self.user))

	def getUnsplashImg(self, content):
		if len(content)>1:
			theme = content[1]
			url = 'https://source.unsplash.com/random/?'+theme
		else:
			url = 'https://source.unsplash.com/random/?background'
		response = urllib.request.urlopen(url)
		if response:
			return response
	async def getWallheaven(self, content, message):
		def getFullPage(imgs, context, urls, quantity, query, resolution):
			imgs.clear()
			if len(query)>1 and len(resolution)>1:
				url = "https://wallhaven.cc/search?"+query+"&"+resolution
				print(url)
			elif len(query)>1:
				url = "https://wallhaven.cc/search?"+query
			else:
				url = urls[context[0]]
			page = requests.get(url)
			soup = BeautifulSoup(page.content, "html.parser")
			results = soup.find(id="thumbs")
			a = results.find_all("a", class_="preview")
			count = 0
			for img in a:
				if count < quantity:
					page_url = img["href"]
					imgs.append(page_url)
					count += 1

		def getSmallJpg(imgs, context, urls, quantity, query, resolution):
			imgs.clear()
			if len(query)>1 and len(resolution)>1:
				url = "https://wallhaven.cc/search?"+query+"&"+resolution
				print(url)
			elif len(query)>1:
				url = "https://wallhaven.cc/search?"+query
			else:
				url = urls[context[0]]
			page = requests.get(url)
			soup = BeautifulSoup(page.content, "html.parser")
			results = soup.find(id="thumbs")
			a = results.find_all("img")
			count = 0
			for img in a:
				if count < quantity:
					img_url = img["data-src"]
					imgs.append(img_url)
					count += 1	

		async def getPngAndJpg(imgs, context, urls, message, quantity, query, resolution):
			imgs.clear()
			if len(query)>1 and len(resolution)>1:
				url = "https://wallhaven.cc/search?"+query+"&"+resolution
				print(url)
			elif len(query)>1:
				url = "https://wallhaven.cc/search?"+query
			else:
				url = urls[context[0]]
			page = requests.get(url)
			soup = BeautifulSoup(page.content, "html.parser")
			results = soup.find(id="thumbs")
			a = results.find_all("a", class_="preview")
			count = 0
			for img in a:
				if count < quantity:
					link_url = img["href"]
					link = re.sub(r'^https?:\/\/.*[\r\n]*\/', '', link_url, flags=re.MULTILINE)
					print('quantity: {} - count: {}'.format(quantity, count))
					full_url = "https://w.wallhaven.cc/full/{}/wallhaven-{}.png".format(link[:2], link)
					wall = requests.get(full_url)				
					if wall.ok:
						imgs.append(full_url)
					else:
						full_url = "https://w.wallhaven.cc/full/{}/wallhaven-{}.jpg".format(link[:2], link)
						imgs.append(full_url)
					count += 1
			return imgs[0:quantity]
		query = ''
		resolution = ''
		context = []
		imgs = []
		sizes = {
			"small": getSmallJpg,
			"large": getPngAndJpg,
			"page": getFullPage
		}
		size = 'page'
		urls = {
			"random": "https://wallhaven.cc/random",
			"toplist":"https://wallhaven.cc/search?categories=110&purity=100&atleast=1920x1080&ratios=16x9&topRange=1M&sorting=toplist&order=desc"
		}
		if len(content) == 1:
			quantity = 1
			context.append('random')
			sizes[size](imgs, context, urls, quantity, query, resolution)
		elif len(content)>=1:
			for word in content:
				if word.startswith('q='):
					query = word
				if word.startswith('atleast='):
					resolution = word
			try:
				quantity = content[-1:]
				quantity = int(quantity[0])
				if quantity > 24:
					await message.channel.send(':octagonal_sign: only 24 images!')
				if 'toplist' in content:
					context.append('toplist')
				else:
					context.append('random')				
			except ValueError:
				quantity = 1
				context.append('random')
				await message.channel.send(':octagonal_sign: the last operator must be a integer')
				sizes[size](imgs, context, urls, quantity, query, resolution)
			if len(content) >= 3:
				size = ''
				for size in sizes:
					if str(size) in content:
						print(size in content)
						size = size
						print(size)
						await sizes[size](imgs, context, urls, message, quantity, query, resolution) if size == 'large' else sizes[size](imgs, context, urls, quantity, query, resolution)
		else:
			quantity = 1
			context.append('random')
			sizes[size](imgs, context, urls, quantity, query, resolution)
		#url = 'https://wallhaven.cc/random'		
		return imgs[0:quantity]

	def premiumCheck(self, author):
		user = author
		if user in self.premium:
			print('user: ',user)
			return user
		else:
			if user in self.users:
				print('user: ',user)
				return False
			else:
				self.users.append(user)
				return user

	async def on_message(self, message):
		#messages = Person(nick=message.author, message=message.content)
		split = lambda x : x.split(' ')
		content = split(message.content)
		if '!u' in content:
			response = self.getUnsplashImg(content)		
			await message.channel.send('There you go:')
			await message.channel.send(response.geturl())
		if '!w' in content:
			premium = self.premiumCheck(str(message.author))
			if premium:
				try:
					response = await self.getWallheaven(content, message)
					for img in response:
						await message.channel.send(img)
						print('sending: ', img)
				except ValueError as error:
					print('error: ',error)
			else:
				await message.channel.send('https://i.pinimg.com/originals/d0/d1/12/d0d112b90a513356e0b2ebb73744ffdb.jpg')
				return await message.channel.send('If you want more, may you want to become premium: https://xsd.xs ;/')
		if '!help' in content:
			if len(content) == 1:
				await message.channel.send('https://pbs.twimg.com/media/Cyei2RgUoAAHJyt.jpg')
				await message.channel.send('''
**"Why did you call?"**
> *!help unsplash* - show unsplash help menu
> *!help wallhaven* - show wallhaven help menu
''')
			elif len(content)>=1:
				for word in content:
					if word.startswith('unsplash'):
						await message.channel.send('https://c.tenor.com/6hVEKMxmQLUAAAAC/cat-laptop.gif')
						await message.channel.send('**This is Charlie, he just work on a full-time job at unsplash, try to be gentle**')
						await message.channel.send('''
> *!u (term)* - search for images on unsplash
> here are some examples:	
>	*!u* mountains,dark
>	*!u* supra
>	*!u* background,nature
> by default unsplash look for -> background
''')
					if word.startswith('wallhaven'):
						await message.channel.send('https://c.tenor.com/CrWHpzxIZYEAAAAC/cat-typing-gif.gif')
						await message.channel.send('**This is Oliver, hes gonna find you wallpaper just please dont upset him**')
						await message.channel.send('''
> *!w (optional:list) (query) (size) (num)* - search for wallhaven images (24)
> here are some examples: 
>	*!w* toplist small 2
>	*!w* large 1
>	*!w* toplist 5
>	*!w* q=anime,dark atleast=1920x1080
>	*!w* q=anime&purity=100&order=desc
> 
> **size:** these sizes refer to return of the image on the chat
>	*small*: small size image
>	*large*: large size image with direct link
>	*page*:  the page of image
> by default -> page
> 
> **list:** refer to wallhaven list sorts | if you're using a query, lists won't work
>	*toplist*: wallhaven toplist wallpapers 
>	*random*:  wallhaven random wallpapers
> by default -> random
> 
> **queries:** you can pass arguments to especify images properties
>	*q=*: you can create youre own query using q=<query>
>	*atleast=*: use atleast to especify resolutions
> by default -> nothing
> 
> **num:** an integer number who goes on the latest [1 .. 24]
> by default -> 1
> if you're not a premium user, can only do it twice
''')
		else:
			msg = ':flushed:'
			if not message.content == msg:
				if str(message.author) in self.friends:
					#return await message.channel.send(msg)
					return print('{0.author}: {0.content}'.format(message))
				else:
					return print('{0.author} - not friend - {0.content}'.format(message))					
			else:
				return
				print('{0.author} - friend - {0.content}'.format(message))

		return print('{0.author}: {0.content}'.format(message))

client = MyClient()

if __name__=='__main__':
	bot = eval(config('BOT'))
	client.run(config('TOKEN'), bot=bot)