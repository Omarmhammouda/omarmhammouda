export class EmailModel {
  public firstName: string;
  public lastName: string;
  public senderEmail: string;
  public emailSubject: string;
  public message: string;

  constructor() {
    this.firstName = '';
    this.lastName = '';
    this.senderEmail = '';
    this.emailSubject = '';
    this.message = '';
  }
}
