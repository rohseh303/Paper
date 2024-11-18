import React from 'react';
import TemplateGallery from '../TemplateGallery';

export default {
  title: 'TemplateGallery',
  component: TemplateGallery,
};

const Template = (args) => <TemplateGallery {...args} />;

export const Default = Template.bind({});
Default.args = {
  // Add any props you want to pass to the TemplateGallery here
}; 