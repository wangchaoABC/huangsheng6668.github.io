import requests

header = {
	
}


def get_js(url):
	response = requests.get(url)
	print(response.text)

if __name__ == "__main__":
	get_js('https://www.zhipin.com/job_detail/?query=android%E9%80%86%E5%90%91&city=101280600&industry=&position=')