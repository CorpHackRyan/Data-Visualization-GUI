import requests
import secrets
import math
import json


def process_data(url: str):
    page_counter = 0
    final_url = f"{url}&api_key={secrets.api_key}&page={page_counter}"

def export_data(x1: str, x2: str, x3: str):




def get_metadata(url: str):
    final_data = []
    final_url = f"{url}&api_key={secrets.api_key}&page=0"
    response = requests.get(final_url)

    if response.status_code != 200:
        print(response.text)
        return[]

    json_data = response.json()

    total_results = json_data["metadata"]["total"]
    current_page = json_data["metadata"]["page"]
    results_per_page = json_data["metadata"]["per_page"]
    total_pages = total_results / results_per_page


    print(total_results, current_page, results_per_page, math.ceil(total_pages))

    # All the results on each page in a singular list returned
    each_page_data = json_data["results"]

    # final_data.extend(each_page_data)
    # return final_data //(goes with the main() part/ for school_data in all_data)


    for page_counter in range(3):
        for school_data in each_page_data:
            print(school_data)
            with open('school_export.txt', 'a') as export_file:
                json.dump(school_data, export_file)
                export_file.write("\n")


def main():
    url = "https://api.data.gov/ed/collegescorecard/v1/schools.json?school.degrees_awarded.predominant=2,3&fields=school.name,school.city,2018.student.size,2017.student.size,2017.earnings.3_yrs_after_completion.overall_count_over_poverty_line,2016.repayment.3_yr_repayment.overall"
    all_data = get_metadata(url)
    # for school_data in all_data:
    #    print(school_data)


if __name__ == '__main__':
    main()





