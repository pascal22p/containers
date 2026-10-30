const repositories = require('./repositories.json');
const registryUrls = require('./registryUrls.json');

module.exports = {
  platform: "github",
  onboarding: false,
  requireConfig: "optional",

  prHourlyLimit: 10,        // Allow up to 10 PRs per hour
  prConcurrentLimit: 5,     // Max open PRs at the same time
  branchConcurrentLimit: 5, // Max branches being processed at once

  extends: [
    "group:allNonMajor"
  ],

  packageRules: [
    {
      "description": "Allow only Scala 3.3.x versions",
      "matchManagers": ["sbt"],
      "matchPackageNames": ["org.scala-lang:scala3-library_3"],
      "allowedVersions": "/^3\\.3\\.\\d+$/"
    },
    {
      "description": "Prevent sbt upgrades to 2.x",
      "matchManagers": ["sbt"],
      "matchFileNames": ["project/build.properties"],
      "allowedVersions": "<2.0.0"
    },
    {
      matchDatasources: ["sbt-package", "sbt-plugin", "maven"],
      registryUrls: [
        "https://repo1.maven.org/maven2",
        "https://repo.scala-sbt.org/scalasbt/sbt-plugin-releases"
      ].concat(registryUrls)
    }
  ],

  repositories: repositories
};


