import React from 'react';
import { render, screen } from '@testing-library/react';
import TemplateGallery from '../TemplateGallery'; // Adjust the path if necessary
import '@testing-library/jest-dom'; // This is sufficient

describe('TemplateGallery Component', () => {
  test('renders the TemplateGallery component', () => {
    render(<TemplateGallery />);
    
    // Check if the component renders correctly
    const headingElement = screen.getByText(/start a new document/i); // Adjust based on your component's content
    expect(headingElement).toBeInTheDocument();

    // Check if the templates are rendered
    const templateElements = screen.getAllByRole('heading', { level: 3 }); // Assuming template names are in <h3>
    expect(templateElements.length).toBeGreaterThan(0); // Ensure at least one template is rendered
  });
}); 