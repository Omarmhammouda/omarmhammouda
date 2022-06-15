import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'omarmhammouda'; 
  clientHeight: number;

constructor() {
   this.clientHeight = window.innerHeight; 
}
}