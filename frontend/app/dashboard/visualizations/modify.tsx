import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from "@/components/ui/dialog";
import { SquarePen } from "lucide-react";

export function ModifyGraphDialog() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="w-fit">
          <SquarePen className="mr-1 h-4 w-4" />
          Customize View
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Modify</DialogTitle>
          <DialogDescription>
            Select which graphs you want to display on your dashboard.
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          <p>Graph selection options...</p>
        </div>
        <DialogFooter className="flex justify-end gap-2">
          <DialogClose asChild>
            <Button type="button" variant="secondary">
              Cancel
            </Button>
          </DialogClose>

          <DialogClose asChild>
            <Button type="submit">Okay</Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
