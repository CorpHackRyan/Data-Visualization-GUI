import requests
import secrets
import math
import json


def process_data(url: str, meta_from_main):
    # meta_from_main is a list with the following index descriptions
    #                 0 index = total results
    #                 1 index = current page
    #                 2 index = results per page
    #                 3 index = total pages
    # return [total_results, current_page, results_per_page, math.ceil(total_pages)]

    page_counter = 0
    final_url = f"{url}&api_key={secrets.api_key}&page={page_counter}"

    # meta_from_main[3] = 2

    for page_counter in range(meta_from_main[3]):
        response = requests.get(final_url)

        if response.status_code != 200:
            print(response.text)
            return []

        json_data = response.json()

        # All the results on each page in a singular list returned
        each_page_data = json_data["results"]

        for school_data in each_page_data:
            print(school_data)
            with open('school_export.txt', 'a') as export_file:
                json.dump(school_data, export_file)
                export_file.write("\n")

        page_counter += 1
        final_url = f"{url}&api_key={secrets.api_key}&page={page_counter}"


def write_data(x1: str, x2: str, x3: str):
    pass


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

    # All the results on each page in a singular list returned
    each_page_data = json_data["results"]

    return [total_results, current_page, results_per_page, math.ceil(total_pages)]


def main():
    url = "https://api.data.gov/ed/collegescorecard/v1/schools.json?school.degrees_awarded.predominant=2,3&fields=school.name,school.city,2018.student.size,2017.student.size,2017.earnings.3_yrs_after_completion.overall_count_over_poverty_line,2016.repayment.3_yr_repayment.overall"
    file_name = "school_export.txt"

    meta_data = get_metadata(url)
    process_data(url, meta_data)

    print(meta_data)


if __name__ == '__main__':
    main()





