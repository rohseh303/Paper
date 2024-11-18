import React from 'react';

const templates = [
  {
    id: 1,
    name: 'Blank',
    description: 'Start fresh with an empty document',
    image: 'https://images.unsplash.com/photo-1531403009284-440f080d1e12?auto=format&fit=crop&w=300&q=80'
  },
  {
    id: 2,
    name: 'Project Proposal',
    description: 'Professional template for project proposals',
    image: 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=300&q=80'
  },
  {
    id: 3,
    name: 'Resume',
    description: 'Clean and modern resume template',
    image: 'https://images.unsplash.com/photo-1586281380349-632531db7ed4?auto=format&fit=crop&w=300&q=80'
  },
  {
    id: 4,
    name: 'Meeting Notes',
    description: 'Structured template for meeting minutes',
    image: 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=300&q=80'
  }
];

const TemplateGallery = () => {
  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Start a new document</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {templates.map((template) => (
          <div
            key={template.id}
            className="group cursor-pointer"
          >
            <div className="aspect-w-16 aspect-h-9 mb-3">
              <img
                src={template.image}
                alt={template.name}
                className="w-full h-full object-cover rounded-lg group-hover:opacity-90 transition-opacity"
              />
            </div>
            <h3 className="font-medium text-gray-900 group-hover:text-blue-600">
              {template.name}
            </h3>
            <p className="text-sm text-gray-500">{template.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TemplateGallery;