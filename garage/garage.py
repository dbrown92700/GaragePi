#!/usr/bin/python3

import pigpio
from flask import Flask, render_template, make_response, redirect
from time import sleep
from threading import Thread

pi = pigpio.pi()
door_button = 17
open_pin = 24
closed_pin = 25
pi.set_mode(door_button, pigpio.OUTPUT)
pi.set_pull_up_down(door_button, pigpio.PUD_DOWN)
pi.write(door_button, 0)
pi.set_mode(open_pin, pigpio.INPUT)
pi.set_pull_up_down(open_pin, pigpio.PUD_UP)
pi.set_mode(closed_pin, pigpio.INPUT)
pi.set_pull_up_down(closed_pin, pigpio.PUD_UP)
door_status = ''
moving_status = 'Unknown'
moving_time = 0


def read_door():

	global pi
	global door_status
	global moving_status
	global moving_time

	while True:
		g_open = pi.read(open_pin)
		g_closed = pi.read(closed_pin)
		if moving_time > 0:
			moving_time -= 1
		if moving_time < 12:
			if g_open == 0:
				door_status = 'Open'
			elif g_closed == 0:
				door_status = 'Closed'
			elif (moving_time == 0) and (door_status != 'Stopped'):
				door_status = 'Stuck??'
		sleep(1)


door_thread = Thread(target=read_door)
door_thread.start()


def push_button(this_button=door_button):

	pi.write(this_button, 1)
	sleep(1)
	pi.write(this_button, 0)


app = Flask(__name__)
app.secret_key = 'any random string'


@app.route('/')
def garage():

	return make_response(render_template('garage.html', status=door_status))


@app.route('/status')
def pin_status():
	global door_status

	return door_status


@app.route('/button')
def button_push():
	global door_status
	global moving_time

	if door_status == 'Open':
		door_status = 'Closing'
	elif door_status == 'Closed':
		door_status = 'Opening'
	elif door_status == 'Closing':
		door_status = 'Stopped'
	elif door_status == 'Opening':
		door_status = 'Closing'
	elif door_status == 'Stopped':
		door_status = 'Opening'
	moving_time = 15

	push_button(door_button)

	return make_response(redirect('/garage'))


if __name__ == '__main__':

	app.run(port=5000)
