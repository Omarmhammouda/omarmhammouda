import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { Observable } from 'rxjs';

import { EmailModel } from '../models';

@Injectable({
  providedIn: 'root'
})
export class EmailService {

  private emailApiEndpoint = 'someUrl.com/emailendpoint';

  constructor(
    private httpClient: HttpClient
    ) { }

  public sendEmail(email: EmailModel): Observable<any>{
    return this.httpClient.post(this.emailApiEndpoint, email);
  }
}
