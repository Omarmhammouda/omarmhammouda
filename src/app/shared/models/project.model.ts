export class ProjectModel {
  public name: string;
  public image: string;
  public video: string;
  public description: string[];
  public link: string;

  constructor() {
    this.name = '';
    this.image = '';
    this.video = '';
    this.description = [];
    this.link = '';
  }
}
