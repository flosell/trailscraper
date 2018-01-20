# Contribution Guide

Thanks for wanting to help out! This project only succeeds because people like you keep on improving it. 

This guide is trying to get you started. It contains helpful guidelines, not hard rules. 
If you aren't sure about something, just ask! 

## I want to help but I don't know what to do

Have a look at the [issue tracker](https://github.com/flosell/trailscraper/issues), maybe you'll find something interesting there.
The [help wanted](https://github.com/flosell/trailscraper/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) and 
[good first issue](https://github.com/flosell/trailscraper/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
labels track issues that make good starting points. 

If nothing in there looks interesting, have a look at [`unknown_actions.txt`](./unknown_actions.txt). 
It contains a list of IAM Actions that TrailScraper generated but that can't be found in unofficial IAM documentation.
Try digging into the AWS documentation to figure out why that is. 

If TrailScraper maps API calls to the wrong IAM actions, open an issue with what you found. 
This alone is very valuable already as finding all the special cases in AWS is most of the effort in this project.
Of course, if you want to invest some more time, PRs with a fix are just as appreciated!
 
If you find that a valid IAM action turns up on that list, it's probably missing in the data source we are using.
Most of that comes from [Widdix IAM Reference](https://iam.cloudonaut.io/) so if you found something that's missing there, 
[contributing](https://github.com/widdix/complete-aws-iam-reference/blob/master/CONTRIBUTING.md) to that documentation helps both projects
  

## How to open the perfect issue

* Be specific and as detailed as you feel is necessary to understand the topic 
* Provide context (what were you trying to achive, what were you expecting, ...)
* Code samples and logs can be really helpful. Consider [Gists](https://gist.github.com/) or links to other Github repos
  for larger pieces. 
* If the UI behaves in a strange way, have a look at your browsers development tools. The console and network traffic might give you some insight that's valuable for a bug report.  
* If you are reporting a bug, add steps to reproduce it. 

## How to create the perfect pull request

* Have a look into the [`README`](README.md#development) for details on how to work with the
  code
* Follow the usual best practices for pull requests: 
  * use a branch, 
  * make sure you have pulled changes from upstream so that your change is easy to merge
  * follow the conventions in the code
  * keep a tidy commit history that speaks for itself, consider squashing commits where appropriate
* Run all the tests: `./go test`
* Add tests where possible
* Add an entry in [`CHANGELOG.md`](CHANGELOG.md) if you add new features, fix bugs or otherwise change LambdaCD in a way that you want 
  users to be aware of. The entry goes into the section for the next release (which is the version number indicated in 
  `project.clj`), usually the top one. If that section doesn't exist yet, add it. 
