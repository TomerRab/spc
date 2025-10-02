import { Check, ExternalLink, Copy } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { CreateProjectResponse, ProjectRepository, LegacyProjectRepository } from '@/types/gitlab';

interface ProjectSuccessDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  createdProject: CreateProjectResponse | null;
  onCopyToClipboard: (text: string) => void;
}

export const ProjectSuccessDialog = ({
  open,
  onOpenChange,
  createdProject,
  onCopyToClipboard
}: ProjectSuccessDialogProps) => {
  if (!createdProject) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-green-600">
            <Check className="h-6 w-6" />
            Project Created Successfully! 🎉
          </DialogTitle>
          <DialogDescription>
            Your project has been created with all the necessary templates and configurations.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Project Summary */}
          {createdProject?.summary && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-green-600 font-medium">{createdProject.summary.message}</span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                <div>Repositories: <span className="font-medium">{createdProject.summary.repos_created}</span></div>
                <div>Files Created: <span className="font-medium">{createdProject.summary.total_files}</span></div>
                {createdProject.summary.environments && (
                  <div className="col-span-2">
                    Environments: <span className="font-medium">{createdProject.summary.environments.join(', ')}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Repository Links */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Repository Links</h3>
            
            {createdProject?.primary_repos ? (
              createdProject.primary_repos.map((repo: ProjectRepository, index: number) => (
                <div key={index} className="border rounded-lg p-6 bg-white shadow-sm">
                  <div className="flex items-center gap-3 mb-3">
                    <h4 className="text-xl font-semibold">{repo.title}</h4>
                  </div>
                  <p className="text-gray-600 mb-4">{repo.description}</p>
                  
                  <div className="space-y-3">
                    <div className="flex items-center gap-3 flex-wrap">
                      <Button asChild className="bg-blue-600 hover:bg-blue-700">
                        <a 
                          href={repo.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="flex items-center gap-2"
                        >
                          <ExternalLink className="h-4 w-4" />
                          Open Repository
                        </a>
                      </Button>
                      <span className="text-sm text-gray-500">({repo.action_text})</span>
                    </div>
                    
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <label className="text-sm font-medium text-gray-700">Clone Command:</label>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => onCopyToClipboard(repo.clone_command)}
                          className="flex items-center gap-1"
                        >
                          <Copy className="h-3 w-3" />
                          Copy
                        </Button>
                      </div>
                      <code className="block bg-gray-100 p-3 rounded text-sm font-mono break-all">
                        {repo.clone_command}
                      </code>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              // Fallback for old API response format
              createdProject?.repositories?.map((repo: LegacyProjectRepository, index: number) => (
                <div key={index} className="border rounded-lg p-6 bg-white shadow-sm">
                  <div className="flex items-center gap-3 mb-3">
                    <h4 className="text-lg font-semibold">{repo.name}</h4>
                  </div>
                  <div className="flex items-center gap-3">
                    <Button asChild className="bg-blue-600 hover:bg-blue-700">
                      <a 
                        href={repo.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="flex items-center gap-2"
                      >
                        <ExternalLink className="h-4 w-4" />
                        Open Repository
                      </a>
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Next Steps */}
          {createdProject?.next_steps && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-medium text-blue-800 mb-2">Next Steps:</h4>
              <ol className="list-decimal list-inside space-y-1 text-sm text-blue-700">
                {createdProject.next_steps.map((step: string, index: number) => (
                  <li key={index}>{step}</li>
                ))}
              </ol>
            </div>
          )}
        </div>

        <div className="flex justify-end mt-6">
          <Button onClick={() => onOpenChange(false)} className="px-8">
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};