from getpass import getpass as get_password
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import datetime

def display_countdown(remaining_time):
    print("Unfollow limit reached for the hour. Waiting...")
    while remaining_time > 0:
        minutes, seconds = divmod(remaining_time, 60)
        seconds = int(seconds)  # Convert seconds to an integer
        minutes = int(minutes)  # Convert minutes to an integer
        print(f"\rTime remaining: {minutes:02d}:{seconds:02d}", end="")
        time.sleep(1)
        remaining_time -= 1
    print("\nHourly limit reset. Resuming unfollow process.")


def handle_prompts(driver):
    max_retries = 3
    retries = 0

    while retries < max_retries:
        try:
            # Handle the "Save Your Login Info" prompt
            driver.find_element("xpath", "//div[@role='button']").click()
            time.sleep(2)

            # Handle the "Turn on Notifications" prompt
            driver.find_element("xpath", "//button[contains(.,'Not Now')]").click()
            time.sleep(2)

            break
        except NoSuchElementException:
            retries += 1
            print("Failed to handle prompts. Retrying...")
            time.sleep(1)


def login(username, password):
    # Launch the web browser and navigate to Instagram
    driver = webdriver.Chrome()  # or webdriver.Firefox() for Firefox
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(4)
    
    # Handle the cookies prompt if it appears
    try:
        driver.find_element("xpath", "//button[contains(.,'Allow all cookies')]").click()
        time.sleep(.5)
    except:
        pass
    
    
    # Find the username and password fields, and enter your login credentials
    username_field = driver.find_element("xpath", "//input[@aria-label='Phone number, username, or email']")
    username_field.send_keys(username)
    password_field = driver.find_element("xpath", "//input[@aria-label='Password']")
    password_field.send_keys(password)

    # Submit the form
    password_field.send_keys(Keys.RETURN)
    time.sleep(2)
    
    # Handle the prompts
    handle_prompts(driver)

    return driver


def get_unfollowers(driver, following_file, followers_file):
    # Read the contents of the following.txt and followers.txt files
    with open(following_file, "r") as file:
        following = file.read().splitlines()
    file.close()

    with open(followers_file, "r") as file:
        followers = file.read().splitlines()
    file.close()
    
    # Determine the unfollowers by comparing the lists
    unfollowers = list(set(following) - set(followers))

    # Write the unfollowers to unfollowers.txt
    with open("unfollowers.txt", "a") as file:
        file.write("\n".join(unfollowers))
    file.close()
    return unfollowers


def unfollow_users(driver, unfollowers_file, daily_limit, hourly_limit, max_retries=3):
    with open(unfollowers_file, "r") as file:
        unfollowers = file.read().splitlines()
    file.close()
    
    # Confirm with the user before proceeding
    confirmation = input(f"Unfollowing {len(unfollowers)} users. Do you want to proceed? (y/n): ")
    if confirmation.lower() != "y":
        print("Unfollow process cancelled.")
        return

    unfollow_count = 0  # Track the number of unfollows
    start_time = datetime.datetime.now()  # Track the start time
    hourly_limit_duration = 1800  # hour(s) in seconds # Change this

    for username in unfollowers:
        if unfollow_count >= daily_limit:
            print("Daily unfollow limit reached. Exiting...")
            break

        if unfollow_count > 0 and unfollow_count % hourly_limit == 0:
            elapsed_time = datetime.datetime.now() - start_time
            if elapsed_time.total_seconds() < hourly_limit_duration:
                display_countdown(hourly_limit_duration)
                start_time = datetime.datetime.now()

        profile_url = f"https://www.instagram.com/{username}/"
        driver.get(profile_url)

        time.sleep(2)

        retries = 0
        while retries < max_retries:
            try:
                # Click the 1st button(Following) then pops a list of actions
                following_button = driver.find_element("xpath", "//button[contains(.,'Following')]")
                following_button.click()
                time.sleep(2)
                
                # Click the 2nd unfollow button(Actual Unfollow)
                try:
                    unfollow_button = driver.find_element("xpath", "//span[contains(., 'Unfollow')]")
                    time.sleep(1)
                    unfollow_button.click()

                    # Wait for the unfollow process to complete
                    time.sleep(6)
                    unfollow_count += 1  # Increment the unfollow count
                except NoSuchElementException:
                    print(f"Unable to find the 'Unfollow' button for user: {username}. Skipping...")
                    continue

            except NoSuchElementException:
                print(f"Unable to find the 'Following' button for user: {username}. Retrying...")
                retries += 1
                time.sleep(2)

        if retries == max_retries:
            print(f"Exceeded maximum retries for user: {username}. Moving on to the next user.")
    
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
    
    daily_limit = 120 # Change this
    hourly_limit = 30 # Change this
    
    unfollow_users(driver, unfollowers_file, daily_limit, hourly_limit)
    print("Unfollow process complete. Script will now Exit.")


if __name__ == "__main__":
    main()
