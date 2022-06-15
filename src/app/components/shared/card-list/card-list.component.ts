import { Component, Input, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ProjectModel } from '../../../shared/models';

@Component({
  selector: 'app-card-list',
  templateUrl: './card-list.component.html',
  styleUrls: ['./card-list.component.css']
})
export class CardListComponent implements OnInit {

  @Input() data: ProjectModel[] = [];

  constructor(private router: Router) { }

  ngOnInit(): void {
  }

  public goTo(link: string): void {
    this.router.navigate([link]);
  }

}
