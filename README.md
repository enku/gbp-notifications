# gbp-notifications

gbp-notifications is a plugin for [Gentoo Build
Publisher](https://github.com/enku/gentoo-build-publisher) that can send
notifications when various events occur in a GBP instance. This is to scratch
my personal itch where i want to receive emails when certain machines have new
builds pulled.

<p align="center">
<img src="https://raw.githubusercontent.com/enku/gbp-notifications/master/docs/screenshot.png" alt="Email Notification" width="100%">
</p>


# Installation

This assumes you already have a working Gentoo Build Publisher installation.
If not refer to the [GBP Install
Guide](https://github.com/enku/gentoo-build-publisher/blob/master/docs/how-to-install.md#gentoo-build-publisher-install-guide)
first.

Install the gbp-notifications package onto the GBP instance.

```
cd /home/gbp
sudo -u gbp -H ./bin/pip install gbp-notifications
```

Restart your web app.

```sh
systemctl restart gentoo-build-publisher-wsgi.service
```

# Configuration

## Environment variables

Like Gentoo Build Publisher itself, gbp-notifications relies on environment
variables for configuration. It looks at variables with a `GBP_NOTIFICATIONS_`
prefix. For example to set up a recipient to receive email notifications when
a build for the machine "babette" gets pulled:

```sh
# /etc/gentoo-build-publisher.conf

GBP_NOTIFICATIONS_RECIPIENTS="albert:email=marduk@host.invalid"
GBP_NOTIFICATIONS_SUBSCRIPTIONS="babette.build_pulled=albert"

GBP_NOTIFICATIONS_EMAIL_FROM="marduk@host.invalid"
GBP_NOTIFICATIONS_EMAIL_SMTP_HOST="smtp.email.invalid"
GBP_NOTIFICATIONS_EMAIL_SMTP_USERNAME="marduk@host.invalid"
GBP_NOTIFICATIONS_EMAIL_SMTP_PASSWORD="supersecret"
```

The first two lines are setting up recipients and subscriptions. There is a
single recipient named `albert` that has an email address. The second line
sets up subscriptions. There is one subscription: when the machine "babette"
receives a `build_pulled` event the the recipient with the name `"albert"`
will be notified. Since `"albert"` has one notification method defined (email)
that recipient will be notified via email.

The wildcard is supported for machines and events, on subscriptions. So
`*.build_pulled=albert` means "send a notification to `albert` when any machine receives
a `build_pulled` event" and `babette.*=albert` means "send a notification to `albert`
when any event is receive for the machine `babette`.  The double-wildcard, `*.*=albert`
does what you'd think.  Notifications are only sent once per recipient (per notification
method).

The last lines are settings for the email notification method.
gbp-notifications has support for multiple notification methods but currently
only email is implemented.

## Config file for Recipients and Subscriptions

Alternatively you can use a toml-formatted config file for recipients and
subscriptions.  For that instead define the `GBP_NOTIFICATIONS_CONFIG_FILE`
environment variable that points to the path of the config file, e.g.

```sh
GBP_NOTIFICATIONS_CONFIG_FILE="/etc/gbp-subscribers.toml"
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

## Webhook method

In addition to email, gbp-notifications supports web hooks. For example,
consider the environment variables:

```
GBP_NOTIFICATIONS_RECIPIENTS="marduk:webhook=http://host.invalid/webhook|X-Pre-Shared-Key=1234",
GBP_NOTIFICATIONS_SUBSCRIPTIONS="*.build_pulled=marduk"
```

The subscriber "marduk" is subscribed the `build_pulled` event for all
machines. The recipient for marduk has a "webhook". The configuration for the
web hook has values that are delimited with `"|"`. The first item will be the
URL of the webhook and any remainint items will be HTTP headers used when
requesting the URL. Note that header definitions are to be given in form
`name=value` and not `name: value`.

Webhooks might be used, for example, to automatically update machines whenever
a new build is published. Or perhaps a desktop notification:

![screenshot](https://raw.githubusercontent.com/enku/screenshots/refs/heads/master/gbp-notifications/desktop-notification.png)


## Pushover method

[Pushover](https://pushover.net/) is a service that allows apps to send push
notifications to mobile and other devices. gbp-notifications supports the Pushover
service.  To enable gbp-notifications to sent Pushover notifications you'll need to
create a user account as well as app key for your GBP instance. Then define the
following denvironment variables:

```sh
# /etc/gentoo-build-publisher.conf


GBP_NOTIFICATIONS_PUSHOVER_USER_KEY="[Pushover user key]",
GBP_NOTIFICATIONS_PUSHOVER_APP_TOKEN"="[Pushover app token]",
```

Pushover subscriptions will look like this:

```sh
GBP_NOTIFICATIONS_RECIPIENTS="marduk:pushover=iphone16pro",
GBP_NOTIFICATIONS_SUBSCRIPTIONS="*.build_pulled=marduk"
```

Replacing `"iphone16pro"` with the device name you've registered with Pushover.

![screenshot](https://raw.githubusercontent.com/enku/screenshots/refs/heads/master/gbp-notifications/pushover.png)
