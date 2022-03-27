#!/usr/bin/python3

import pigpio
from flask import Flask, render_template, make_response, redirect
from time import sleep
from threading import Thread

pi = pigpio.pi()
door_button = 17
open_pin = 24
pi.set_mode(door_button, pigpio.OUTPUT)
pi.set_pull_up_down(door_button, pigpio.PUD_DOWN)
pi.write(door_button, 0)
pi.set_mode(open_pin, pigpio.INPUT)
pi.set_pull_up_down(open_pin, pigpio.PUD_DOWN)
door_status = ''


def read_door():

	global pi
	global door_status

	while True:
		gopen = pi.read(open_pin)
		if gopen == 0:
			door_status = 'Closed'
		else:
			door_status = 'Open'
		sleep(0.5)


door_thread = Thread(target=read_door)
door_thread.start()


def push_button(this_button=door_button):

	pi.write(this_button, 1)
	sleep(1)
	pi.write(this_button, 0)


app = Flask(__name__)
app.secret_key = 'any random string'


@app.route('/garage')
def garage():

	return make_response(render_template('garage.html', status=door_status))


@app.route('/status')
def pin_status():

	return door_status


@app.route('/button')
def button_push():

	push_button(door_button)

	return make_response(redirect('/garage'))


if __name__ == '__main__':

	app.run(port=5000)
