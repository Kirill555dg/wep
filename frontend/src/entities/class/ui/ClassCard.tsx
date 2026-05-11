import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/shared/ui/card";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { Link } from "react-router-dom";
import { Teacher } from "@/entities/teacher/model/types";

export interface ClassCardProps {
  id: number;
  name: string;
  teacherName: string;
  activeAssignments: number;
  image: string;
}

export const ClassCard = ({ id, name, teacherName, activeAssignments, image }: ClassCardProps) => {
  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer">
      <div className="h-40 overflow-hidden">
        <img src={image || "/placeholder.svg"} alt={name} className="w-full h-full object-cover object-top" />
      </div>
      <CardHeader className="pb-2">
        <CardTitle>{name}</CardTitle>
        <CardDescription>{teacherName}</CardDescription>
      </CardHeader>
      <CardContent className="pb-2">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Активные задания</span>
          <Badge variant={activeAssignments > 0 ? "default" : "outline"}>{activeAssignments}</Badge>
        </div>
      </CardContent>
      <CardFooter>
        <Link to={`/student/class/${id}`} className="w-full">
          <Button variant="outline" className="w-full">
            Перейти к классу
          </Button>
        </Link>
      </CardFooter>
    </Card>
  );
};
