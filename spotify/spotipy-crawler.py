""" Spotipy Crawler
This scripts reads tracks from a CSV file and consumes the Spotify API to obtain artist and track metadata.
Copyright (C) 2017  Ramiro Savoie ramiro.savoie@gmail.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# Spotipy initialization.
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Data science modules.
import pandas as pd

# For get arguments from command line.
import sys

# For counting genders.
import collections

# For pretty JSON printing.
import json
from pygments import highlight, lexers, formatters

import csv

# Print the response JSON with colors and indents.
# response object is a dictionary
def pretty_response(response):
    formatted_json = json.dumps(response, indent=4)
    print(highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter()))    

# Remove apostrophe and reverse the name and surname.
def format_artist(artist):
	cleaned_artist = artist.replace("'","") # Replace apostrophe
	cleaned_artist = ' '.join(cleaned_artist.split(", ")[::-1]) # Split string with ', ' and reverse it
	return cleaned_artist

# Search only one artist.
def search_artist(artist):
	cleaned_artist = format_artist(artist)
	print("Searching for '" + cleaned_artist + "'")
	results = spotify.search("artist:" + cleaned_artist, type="artist")
	pretty_response(results['artists']['items']) # Most relevant artist is at index 0

# Generate a list with all genres played by the artists
def count_genres(dataframe):
	genres = []
	for artist in dataframe['artist.inverted']:
		cleaned_artist = format_artist(artist)
		print("Searching for " + cleaned_artist)
		results = spotify.search("artist:" + cleaned_artist, type="artist")
		if(not results['artists']['items']): # Empty list check
			print("Unmatched artist!")
		else:
			matched_artist = results['artists']['items'][0] # Most relevant artist is at index 0
			print("Matched with " + matched_artist['name'])
			genres += matched_artist['genres']
			print("Genders played: ")
			pretty_response(matched_artist['genres'])
	return genres

# Get the main genre played by the artist.
def get_main_genre(artist_genres):
	# Simplified model for genres with priority.
	most_common_genres = [
	  #	Primary genres
	  'pop',
	  'r&b',
	  'rock',  
	  'hip hop',
	  'country',
	  'rap',
	  'latin',  
	  'neo soul',
	  'punk',
	  'post-grunge',
	  'alternative rock',
	  'alternative metal',
	  'nu metal',
	  'electronic',
	  'new wave',

	  # Combinations with pop
	  'pop rock',
	  'pop rap',  
	  'dance pop',
	  'hip pop',
	  'europop',
	  'post-teen pop',

	  # Others genres
	  'blues-rock',
	  'gangster rap',
	  'smooth jazz',
	  'soft rock',
	  'canadian pop',
	  'boy band',
	  'deep contemporary country',
	  'disco house',
	  'german techno',
	  'trance'
	]

	# Search for the most common genres in the genres played by the artist.
	selected_genres = [most_common_genre for most_common_genre in most_common_genres if most_common_genre in artist_genres]
	# print("Selected genres: " + str(selected_genres) + "\n")

	# Get only the first genre or return an empty string.
	main_genre = []
	if selected_genres:
		main_genre = selected_genres[0]
		print("Main artist genre: " + main_genre)
	else:
		main_genre = 'NA'
		print("Artist genre not found!")

	return main_genre	

# Search for artists and get his main image, spotify ID and genres played.
def search_for_artists_metadata(dataframe):
	artists_metadata = [] 
	for artist in dataframe['artist.inverted']:
		cleaned_artist = format_artist(artist)
		print("\nSearching for " + cleaned_artist)
		results = spotify.search("artist:" + cleaned_artist, type="artist")
		artist_metadata = []
		if(not results['artists']['items']): # Empty list check.
			print("Unmatched artist!")
			artist_metadata = ['NA', 'NA', 'NA'] # Add a row with all NA
		else:
			matched_artist = results['artists']['items'][0] # Most relevant artist is at index 0
			print("Matched with " + matched_artist['name'])

			# Main artist genre
			artist_genre = get_main_genre(matched_artist['genres'])
			artist_metadata.append(artist_genre)

			# Spotify URI
			artist_metadata.append(matched_artist['uri'])

			# Main artist image
			artist_image = []
			if matched_artist['images']:
				artist_image = matched_artist['images'][0]['url']
				print("Main artist image: " + artist_image)
			else:
				print("Main artist image not found!")	
				artist_image = 'NA'
			artist_metadata.append(artist_image)	

		artists_metadata.append(artist_metadata)		
	return artists_metadata

# Generate a csv file with the genres of dataframe tracks.
def write_csv_artists_metadata(artists):
	with open('spotify-metadata.csv', 'w') as csv_file:
		csv_writer = csv.writer(csv_file)
		# Write header row
		csv_writer.writerow(['spotify.genre', 'artist.id', 'artist.image'])
		for artist in artists:
			csv_writer.writerow(artist)

# Authenticate with Client Credentials Flow
# Put your client_id and client_secret here from https://developer.spotify.com/my-applications/#!/applications
client_credentials_manager = SpotifyClientCredentials(client_id='your_client_id', client_secret='your_client_secret')
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Input dataframe.
dataframe = pd.read_csv('../billboard.csv', encoding='latin=1')

# artist = sys.argv[1] # Read argument from command line
# artist = "Aguilera, Christina"	
# search_artist(artist)

# genres = count_genres(dataframe)
# print(collections.Counter(genres))

artists_metadata = search_for_artists_metadata(dataframe)
print(artists_metadata)
write_csv_artists_metadata(artists_metadata)