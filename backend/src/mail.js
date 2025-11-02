import { MailService } from "@sendgrid/mail";

const sendgridClient = new MailService();

sendgridClient.setApiKey(process.env.SENDGRID_API_KEY);

export async function sendAlertEmail({ bottle_id, volume, threshold }) {
  const msg = {
    to: process.env.ALERT_EMAIL_RECIPIENT,
    from: process.env.FROM_EMAIL,
    subject: `Alert — Bottle ${bottle_id} below threshold`,
    text: `Bottle ${bottle_id}'s volume is currently ${volume} ml, below set threshold of ${threshold}.`,
  };

  await sendgridClient.send(msg);
}
