import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HiyeroComponent } from './hiyero.component';

describe('HiyeroComponent', () => {
  let component: HiyeroComponent;
  let fixture: ComponentFixture<HiyeroComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ HiyeroComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(HiyeroComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
