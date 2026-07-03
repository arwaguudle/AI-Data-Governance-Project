from request_generator.schema import Requests


def create_prompt(domain, datamap, producer, output_port, num_requests, policy):
    messages = [
        {
            'role': 'system',
            'content': f"""As a Senior IT Governance Specialist, you are an expert dedicated to understand how the {domain} business works, what information is processed in {domain} business processess and which divisions work with what kind of data. In this pivotal role, you are entrusted with reviewing, and cataloging the diverse workflows, use cases and business processes in the {domain} industry from a data perspective."""
        },
        {
            'role': 'user',
            'content': f""" Create a comprehensive and self-explanatory list, in JSON format, detailing the various business processes. Each dictionary in the created list describes a particular data access request for the following data product:

                {producer}

 Provide {num_requests} data access requests for business processes for the aforementioned producing data product '{producer['info']['title']}' with the following output port: {output_port} 
 The requests must contain specific details about what data is used, by using action verbs that clearly describe the actions, activities, or processes of the requesting data product or application. 
 The level of specificity should be consistent across all uses.

 For each of these uses, you must output the following elements each. Use around 100 words for the purpose description:
 (1) Title: A concise title of the request
 (2) Purpose: Describe for which use case or business process the data is needed, and why. Highlight the business value and the data requested. Write from the perspective of the consuming team or application. If the request is expected to be rejected, do not state this explicitly.
 (3) Provider: The providing output port of the data product
 (4) Consumer: The data application that requests the data. Choose one of the following teams {", ".join(list(map(lambda t: t['name'].title() + '(id: ' + t['id'] + ')', filter(lambda t: producer['info']['owner'] != t['id'], datamap.teams))))} and create a realistic data application within this team. The producer must be a different team than the consumer team!
 (5) Expected Decision: Whether the access request should be accepted based on the privacy policy.


Ensure that each concept is specific and easy to understand for non-experts.
Avoid duplicate purposes or objectives.
Use clear and precise language to describe the access request.

Make sure to create a wide range of realistic access requests that can be accepted or might be rejected according to the privacy policy: {policy}

Follow this example structure for reporting the identified uses:

title: "Upselling Recommendation Analysis"
purpose: "We want to analyze the current and past contracts to recommend those customers that are most likely to accept an upselling attempt, e.g. an increase of their sum insured, based on their base data (esp. age) and prior medical record (esp. illnesses)"
provider:
  dataProductId: bbdd3607-7be7-4d82-a3c1-190b69fe8cc8
  outputPortId: api
consumer:
  teamId: marketing
  data_application_name: "Upselling Recommendation App"
  data_application_description: "Provides insights about what upselling attempts are most profitable and/or most likely to be accepted by a specific policyholder."
expected_decision: "accept"
 """}
    ]
    return messages


def call_openai(client, messages):
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        n=1,
        messages=messages,
        response_format=Requests
    )

    return response.choices[0].message.content
