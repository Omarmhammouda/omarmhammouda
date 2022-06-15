import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CirrusLedComponent } from './pages/cirrus-led/cirrus-led.component';
import { CommonComponent } from './pages/common/common.component';
import { HiyeroComponent } from './pages/hiyero/hiyero.component';
import { HomeComponent } from './pages/home/home.component';

const routes: Routes = [
  {
    path: '',
    component: HomeComponent
  },
  {
    path: 'hiyero',
    component: HiyeroComponent
  },
  {
    path: 'common',
    component: CommonComponent
  },
  {
    path: 'cirrusled',
    component: CirrusLedComponent
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
