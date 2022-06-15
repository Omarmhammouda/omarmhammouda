import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CirrusLedComponent } from './cirrus-led.component';

describe('CirrusLedComponent', () => {
  let component: CirrusLedComponent;
  let fixture: ComponentFixture<CirrusLedComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CirrusLedComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CirrusLedComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
