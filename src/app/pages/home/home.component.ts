import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

import { Subscription } from 'rxjs';
import { EmailModel, ProjectModel } from 'src/app/shared/models';

import { EmailService } from '../../shared/services/email.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  animations:[]
})
export class HomeComponent implements OnInit, OnDestroy {

  records: ProjectModel[] = [
    {
      name: 'HIYERO',
      image: "./assets/project-thumbnails/hiyero.png",
      video: '',
      description: ['Enhance photos, save time in the shooting process and speed up the perfect shot with mirror technology.'],
      link: "/hiyero",

    },
    {
      name: 'COMMON',
      image: "./assets/project-thumbnails/common.png",
      video: '',
      description: ['Finding affordable housing in the most popular cities in the nation',
        'Searching for what really matters in housing without the worries of cost'],
      link: "/common",

    },
    {
      name: 'CIRRUS LED',
      image: "./assets/project-thumbnails/cirrus-led.png",
      video: '',
      description: ['Design a digital signage software company website for a better user experience.',
        'Seeing through the customer’s eyes and designing the website interface according to the research result'],
      link: "/cirrusled",
    },
    {
      name: 'CORVA',
      image: '',
      video: './assets/corva/corva-video.webm',
      description: ['Comming soon!'],
      link: '',
    }];

  public sendEmailFormGroup: FormGroup;
  public email: EmailModel = new EmailModel();

  private emailServiceSubscription: Subscription = Subscription.EMPTY;

  constructor(
    private emailService: EmailService,
    private formBuilder: FormBuilder) {

      this.sendEmailFormGroup = this.formBuilder.group({
        firstName: ['', Validators.required],
        lastName: ['', Validators.required],
        senderEmail: ['', Validators.required],
        emailSubject: ['', Validators.required],
        message: ['', Validators.required],
      });
  }

  ngOnInit() {

  }

  public onEmailSubmit(): void{
    this.email = this.sendEmailFormGroup.getRawValue();
    if(!this.sendEmailFormGroup?.invalid){
      this.emailService.sendEmail(this.email).subscribe((result) => {
      });
    }
  }

  ngOnDestroy() {
    this.emailServiceSubscription.unsubscribe();
  }
}
