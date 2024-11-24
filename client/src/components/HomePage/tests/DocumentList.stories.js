import React from 'react';
import DocumentList from '../DocumentList';

export default {
  title: 'DocumentList',
  component: DocumentList,
};

const Template = (args) => <DocumentList {...args} />;

export const Default = Template.bind({});
Default.args = {
  // Add any props you want to pass to the DocumentList here
}; 