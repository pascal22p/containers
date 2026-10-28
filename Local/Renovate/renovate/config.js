module.exports = {
  platform: "github",
  onboarding: false,
  requireConfig: "optional",

  gitAuthor: "Renovate Bot <pascal22p@parois.net>",

  prHourlyLimit: 10,        // Allow up to 10 PRs per hour
  prConcurrentLimit: 5,     // Max open PRs at the same time
  branchConcurrentLimit: 5, // Max branches being processed at once

  packageRules: [
    {
      matchDatasources: ["sbt-package"],
      registryUrls: [
        "https://repo.maven.apache.org/maven2",
        "https://open.artefacts.tax.service.gov.uk/maven2/"
      ]
    }
  ],

  repositories: [
    "pascal22p/hmrc-example-uk-fuel"
  ]
};

