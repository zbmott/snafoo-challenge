This is a project I built in response to a Python coding challenge I was given while applying for an engineering position. It doubles as a nice portfolio piece.

I was to take approximately 10 hours to build a simple application that allowed users to vote on which snacks they wanted to eat in a particular month.
- Users were allowed to place 3 votes per month.
- Users were allowed to nominate one snack each month. The snack could either be brand new, or have been nominated in a previous month.

Functional requirements:
- Two views, one for nominating snacks, and one for voting for snacks.
- The voting view must contain the following elements:
  - A list of snacks that are purchased every month, regardless of voting.
  - A list of snacks that are voted on each month. Each snack should display the number of votes received so far this month, the date that the snack was last purchased, and a button to allow the user to cast a vote for the snack.
  - The number of votes the user has remaining in the month.
- Once a user has placed a vote, the user is not allowed to change that vote.
- Users should not be allowed to cast more than the allotted number of votes each month.
- The nomination view must contain the following elements:
  - A dropdown of snacks that have been previously nominated, but that haven't been nominated yet this month. This list should not include any snacks that are mandatory (i.e. purchased every month regardless of voting).
  - A form to submit a nominate a brand new snack.
- Users should not be allowed to nominate more than the allotted number of snacks each month.
- Users should not be allowed to nominate a snack that has already been nominated.
- Both views must make use of an external web service to gather information about the available snacks
- The nomination view should

Non-functional requirements:
- Submission is well-documented and readable.
- Submission respects [PEP8](https://www.python.org/dev/peps/pep-0008/) style guide.
- Submission avoids common web application vulnerabilities (SQL injection, CSRF, XSS).
- Submission displays user-friendly error messages.
- Submission employs semantically valid HTML 5.

Brief discussion:
- I used Django to implement my solution, because that's the framework I have the most expertise with.
- This solution implements approval-style voting, i.e. users can vote for the same snack multiple times.
- This solution requires users to log in in order to nominate or vote for snacks. This ensures that nomination and voting limits are strictly enforced, since nominations and votes are tied to user accounts.
- This solution makes all external web service requests on the server side. Although these could easily be done on the front end, doing so would expose the API key to prying eyes. I chose to protect the API key at the cost of an extra round trip while handling most requests.
- The responses from the web service were clear about their desire not to be cached, so my solution does not cache these.
- This solution decouples the web service from the rest of the application. Interested parties could deploy this application without an external web service. See ``settings.SNACK_SOURCE_CLASS`` and ``snacksdb.utils.AbstractSnackSource``.
- This solution includes a complete test suite.
- This solution includes the Ansible playbook I use to provision and deploy it to its production environment. Sensitive information is protected by the [Ansible Vault](http://docs.ansible.com/ansible/2.5/user_guide/vault.html) mechanism, which uses AES-256 encryption.

As of 2018-05-06, my submission can be found at [snacks.zbmott.net](http://snacks.zbmott.net). Authentication is required to access the voting interface. Ten test accounts are available:
testuser1, testuser2, ..., testuser10. Each accounts password is the same as its username.
