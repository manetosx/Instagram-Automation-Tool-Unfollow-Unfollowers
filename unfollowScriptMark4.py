from getpass import getpass as get_password
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime

def login(username, password):
    # Launch the web browser and navigate to Instagram
    driver = webdriver.Chrome()  # or webdriver.Firefox() for Firefox
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(3)
    
    # Handle the cookies prompt if it appears
    try:
        driver.find_element("xpath", "//button[contains(.,'Allow all cookies')]").click()
        time.sleep(4)
    except:
        pass
    
    # Find the username and password fields, and enter your login credentials
    username_field = driver.find_element("xpath", "//input[@aria-label='Phone number, username, or email']")
    time.sleep(2)
    username_field.send_keys(username)
    password_field = driver.find_element("xpath", "//input[@aria-label='Password']")
    time.sleep(2)
    password_field.send_keys(password)

    # Submit the form
    password_field.send_keys(Keys.RETURN)

    time.sleep(3)  # Add a delay to allow for login
    
    # Handle the "Turn on Notifications" prompt if it appears
    try:
        driver.find_element("xpath", "//button[contains(.,'Not Now')]").click()
        time.sleep(4)
    except:
        pass
    
    # Handle the "Save Your Login Info" prompt if it appears
    try:
        driver.find_element("xpath", "//button[contains(.,'Not Now')]").click()
        time.sleep(4)
    except:
        pass

    return driver

def get_unfollowers(driver, following_file, followers_file):
    # Read the contents of the following.txt and followers.txt files
    with open(following_file, "r") as file:
        following = file.read().splitlines()

    with open(followers_file, "r") as file:
        followers = file.read().splitlines()

    # Determine the unfollowers by comparing the lists
    unfollowers = list(set(following) - set(followers))

    # Write the unfollowers to unfollowers.txt
    with open("unfollowers.txt", "a") as file:
        file.write("\n".join(unfollowers))

    return unfollowers

def unfollow_users(driver, unfollowers_file, daily_limit, hourly_limit):
    with open(unfollowers_file, "r") as file:
        unfollowers = file.read().splitlines()

    # Confirm with the user before proceeding
    confirmation = input(f"Unfollowing {len(unfollowers)} users. Do you want to proceed? (y/n): ")
    if confirmation.lower() != "y":
        print("Unfollow process cancelled.")
        return

    unfollow_count = 0  # Track the number of unfollows
    start_time = datetime.datetime.now()  # Track the start time

    for username in unfollowers:
        if unfollow_count >= daily_limit:
            print("Daily unfollow limit reached. Exiting...")
            break

        if unfollow_count > 0 and unfollow_count % hourly_limit == 0:
            elapsed_time = datetime.datetime.now() - start_time
            if elapsed_time.total_seconds() < 3600:
                remaining_time = 3600 - elapsed_time.total_seconds()
                print(f"Unfollow limit reached for the hour. Sleeping for {int(remaining_time)} seconds...")
                time.sleep(int(remaining_time))
                start_time = datetime.datetime.now()

        profile_url = f"https://www.instagram.com/{username}/"
        driver.get(profile_url)

        time.sleep(2)

        # Click the 1st button(Following) then pops a list of actions
        driver.find_element("xpath", "//button[contains(.,'Following')]").click()
        time.sleep(2)
        # Click the 2nd unfollow button(Actual Unfollow)
        unfollow_button = driver.find_element("xpath","//span[contains(., 'Unfollow')]")
        time.sleep(1)
        unfollow_button.click()

        unfollow_count += 1
        time.sleep(3)

    driver.quit()


def main():
    # Replace 'your_username' and 'your_password' with your actual Instagram credentials
    username = input("Enter your username: ")
    password = get_password("Enter your Instagram password: ")

    # Provide the paths to following.txt and followers.txt
    following_file = "following.txt"
    followers_file = "followers.txt"

    # Log in to your Instagram account
    driver = login(username, password)

    # Determine the unfollowers and save them to unfollowers.txt
    get_unfollowers(driver, following_file, followers_file)         #Comment this out if you want to test with a file ufollowers.txt you already have.

    # Unfollow the users in the unfollowers list
    unfollowers_file = "unfollowers.txt"
    
    # Provide limits and call function
    
    daily_limit = 200 # Change this
    hourly_limit = 25 # Change this
    unfollow_users(driver, unfollowers_file, daily_limit, hourly_limit)
    print("Unfollow process complete. Script will now Exit.")


if __name__ == "__main__":
    main()