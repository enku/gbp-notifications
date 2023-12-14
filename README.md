# gbp-notifications

gbp-notifications is a plugin for [Gentoo Build
Publisher](https://github.com/enku/gentoo-build-publisher) that can send
notifications when various events occur in a GBP instance. This is to scratch
my personal itch where i want to receive emails when certain machines have new
builds pulled.

More to come...

<p align="center">
<img src="https://raw.githubusercontent.com/enku/gbp-notifications/master/docs/screenshot.png" alt="Email Notification" width="100%">
</p>

# Environment variables

Like Gentoo Build Publisher itself, gbp-notifications relies on environment
variables for configuration. It looks at variables with a `GBP_NOTIFICATIONS_`
prefix. For example to set up a recipient to receive email notifications when
a build for the machine "babette" gets pulled:

```sh
GBP_NOTIFICATIONS_RECIPIENTS="albert:email=marduk@host.invalid"
GBP_NOTIFICATIONS_SUBSCRIPTIONS="babette.build_pulled=albert"

GBP_NOTIFICATIONS_EMAIL_FROM="marduk@host.invalid"
GBP_NOTIFICATIONS_EMAIL_SMTP_HOST"=smtp.email.invalid"
GBP_NOTIFICATIONS_EMAIL_SMTP_USERNAME="marduk@host.invalid"
GBP_NOTIFICATIONS_EMAIL_SMTP_PASSWORD="supersecret"
```

The first two lines are setting up recipients and subscriptions. There is a
single recipient named `albert` that has an email address. The second line
sets up subscriptions. There is one subscription: when the machine "babette"
receives a `build_pulled` event the the recipient with the name `"albert"`
will be notified. Since `"albert"` has one notification method defined (email)
that recipient will be notified via email.

The last lines are settings for the email notification method.
gbp-notifications has support for multiple notification methods but currently
only email is implemented.

# Config file for Recipients and Subscriptions

Alternatively you can use a toml-formatted config file for recipients and subscriptions.
For that instead define the `GBP_NOTIFICATIONS_CONFIG` environment variable that points
to the path of the config file, e.g.

```sh
GBP_NOTIFICATIONS_CONFIG="/etc/gbp-subcribers.toml"
```

Then in your config file, the above configuration would look like this:

```toml
[recipients]
albert = {email = "marduk@host.invalid"}

[subscriptions]
babette = {build_pulled = ["albert"]}
```

A more sophisticated example might be:

```toml
[recipients]
# Albert and Bob are recipients with email addresses.
albert = {email = "marduk@host.invalid"}
bob = {email = "bob@host.invalid"}

[subscriptions]
# Both Albert and Bob want to be notified when builds for babette are pulled
babette = {build_pulled = ["albert", "bob"]}

# For lighthouse Albert only wants to be notified when builds are pulled. Bob only wants
# To be notified when builds are published.
lighthouse = {build_pulled = ["albert"], build_published = ["bob"]}
```


# ToDo
- docs
- wildcard support for subscriptions
- more events
- more notification methods
